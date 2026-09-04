from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import shutil, os, tempfile
from datetime import date, datetime
from typing import Optional

from database import engine, get_db, Base
from models import (
    Transaction, Budget, UploadedFile,
    BankConnection, BalanceSnapshot, NetWorthSnapshot,
)
from file_parser import parse_file
import vault
import scraper_bridge
from institutions import SCRAPED_INSTITUTIONS, MANUAL_INSTITUTIONS
from sync_service import sync_connection, record_networth_snapshot
from scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="מתכנן פיננסי - רועי וניקול")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@app.on_event("startup")
def _on_startup():
    start_scheduler()


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    today = date.today()
    current_month = today.strftime("%Y-%m")

    total_all = db.query(func.sum(Transaction.amount)).scalar() or 0
    total_month = (
        db.query(func.sum(Transaction.amount))
        .filter(
            extract("year", Transaction.date) == today.year,
            extract("month", Transaction.date) == today.month,
        )
        .scalar() or 0
    )

    by_category = (
        db.query(Transaction.category, func.sum(Transaction.amount).label("total"))
        .group_by(Transaction.category)
        .all()
    )

    by_person = (
        db.query(Transaction.person, func.sum(Transaction.amount).label("total"))
        .group_by(Transaction.person)
        .all()
    )

    by_month = (
        db.query(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            func.sum(Transaction.amount).label("total"),
        )
        .group_by(func.strftime("%Y-%m", Transaction.date))
        .order_by("month")
        .all()
    )

    top_expenses = (
        db.query(Transaction)
        .order_by(Transaction.amount.desc())
        .limit(5)
        .all()
    )

    budgets = db.query(Budget).filter(Budget.month == current_month).all()
    budget_status = []
    for b in budgets:
        spent = (
            db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.category == b.category,
                func.strftime("%Y-%m", Transaction.date) == current_month,
            )
            .scalar() or 0
        )
        budget_status.append({
            "category": b.category,
            "limit": b.monthly_limit,
            "spent": spent,
            "remaining": b.monthly_limit - spent,
        })

    return {
        "total_all_time": round(total_all, 2),
        "total_this_month": round(total_month, 2),
        "by_category": [{"category": r.category, "total": round(r.total, 2)} for r in by_category],
        "by_person": [{"person": r.person, "total": round(r.total, 2)} for r in by_person],
        "by_month": [{"month": r.month, "total": round(r.total, 2)} for r in by_month],
        "top_expenses": [
            {"id": t.id, "date": str(t.date), "description": t.description,
             "amount": t.amount, "category": t.category, "person": t.person}
            for t in top_expenses
        ],
        "budget_status": budget_status,
    }


# ─── Transactions ─────────────────────────────────────────────────────────────

@app.get("/api/transactions")
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    person: Optional[str] = None,
    month: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = "date",
    sort_dir: str = "desc",
    db: Session = Depends(get_db),
):
    q = db.query(Transaction)
    if category:
        q = q.filter(Transaction.category == category)
    if person:
        q = q.filter(Transaction.person == person)
    if month:
        q = q.filter(func.strftime("%Y-%m", Transaction.date) == month)
    if search:
        q = q.filter(Transaction.description.ilike(f"%{search}%"))

    col = getattr(Transaction, sort_by, Transaction.date)
    q = q.order_by(col.desc() if sort_dir == "desc" else col.asc())

    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [
            {"id": t.id, "date": str(t.date), "description": t.description,
             "amount": t.amount, "category": t.category, "person": t.person,
             "source_file": t.source_file}
            for t in items
        ],
    }


@app.put("/api/transactions/{tx_id}")
def update_transaction(tx_id: int, data: dict, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(404, "לא נמצא")
    for k, v in data.items():
        if hasattr(tx, k):
            setattr(tx, k, v)
    db.commit()
    db.refresh(tx)
    return {"id": tx.id, "category": tx.category, "person": tx.person}


@app.delete("/api/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(404, "לא נמצא")
    db.delete(tx)
    db.commit()
    return {"ok": True}


# ─── Upload ───────────────────────────────────────────────────────────────────

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        rows = parse_file(tmp_path)
    finally:
        os.unlink(tmp_path)

    count = 0
    for r in rows:
        tx = Transaction(
            date=r["date"],
            description=r["description"],
            amount=r["amount"],
            category=r["category"],
            person=r.get("person", "משותף"),
            source_file=file.filename,
        )
        db.add(tx)
        count += 1

    uploaded = UploadedFile(
        filename=file.filename,
        file_type=suffix,
        rows_imported=count,
    )
    db.add(uploaded)
    db.commit()

    return {"filename": file.filename, "imported": count}


@app.get("/api/files")
def get_files(db: Session = Depends(get_db)):
    files = db.query(UploadedFile).order_by(UploadedFile.uploaded_at.desc()).all()
    return [
        {"id": f.id, "filename": f.filename, "file_type": f.file_type,
         "rows_imported": f.rows_imported, "uploaded_at": str(f.uploaded_at)}
        for f in files
    ]


# ─── Budget ───────────────────────────────────────────────────────────────────

@app.get("/api/budget")
def get_budget(month: Optional[str] = None, db: Session = Depends(get_db)):
    if not month:
        month = date.today().strftime("%Y-%m")
    budgets = db.query(Budget).filter(Budget.month == month).all()
    return [{"id": b.id, "category": b.category, "monthly_limit": b.monthly_limit, "month": b.month} for b in budgets]


@app.post("/api/budget")
def set_budget(data: dict, db: Session = Depends(get_db)):
    month = data.get("month", date.today().strftime("%Y-%m"))
    existing = db.query(Budget).filter(Budget.category == data["category"], Budget.month == month).first()
    if existing:
        existing.monthly_limit = data["monthly_limit"]
    else:
        db.add(Budget(category=data["category"], monthly_limit=data["monthly_limit"], month=month))
    db.commit()
    return {"ok": True}


# ─── Stats ────────────────────────────────────────────────────────────────────

@app.get("/api/stats/categories")
def stats_categories(month: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Transaction.category, func.sum(Transaction.amount).label("total"), func.count(Transaction.id).label("count"))
    if month:
        q = q.filter(func.strftime("%Y-%m", Transaction.date) == month)
    q = q.group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc())
    return [{"category": r.category, "total": round(r.total, 2), "count": r.count} for r in q.all()]


# ─── כספת (הצפנת פרטי התחברות לבנקים) ─────────────────────────────────────────

@app.get("/api/vault/status")
def vault_status(db: Session = Depends(get_db)):
    return {"exists": vault.is_setup(db), "unlocked": vault.is_unlocked()}


@app.post("/api/vault/setup")
def vault_setup(data: dict, db: Session = Depends(get_db)):
    password = data.get("password", "")
    if len(password) < 6:
        raise HTTPException(400, "הסיסמה חייבת להכיל לפחות 6 תווים")
    try:
        vault.setup_vault(db, password)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    return {"ok": True}


@app.post("/api/vault/unlock")
def vault_unlock(data: dict, db: Session = Depends(get_db)):
    try:
        vault.unlock_vault(db, data.get("password", ""))
    except ValueError as exc:
        raise HTTPException(401, str(exc))
    return {"ok": True}


@app.post("/api/vault/lock")
def vault_lock_endpoint():
    vault.lock_vault()
    return {"ok": True}


# ─── גופים נתמכים ──────────────────────────────────────────────────────────────

@app.get("/api/institutions")
def list_institutions():
    return {
        "scraped": [
            {"id": k, "name": v["name"], "category": v["category"], "fields": v["fields"], "kind": "scraped"}
            for k, v in SCRAPED_INSTITUTIONS.items()
        ],
        "manual": [
            {"id": k, "name": v["name"], "category": v["category"], "fields": [], "kind": "manual"}
            for k, v in MANUAL_INSTITUTIONS.items()
        ],
        "node_available": scraper_bridge.is_node_available(),
        "scraper_ready": scraper_bridge.is_scraper_ready(),
    }


# ─── חיבורים (בנקים / כרטיסי אשראי / בתי השקעות / ביטוח) ──────────────────────

def _serialize_conn(c: BankConnection):
    return {
        "id": c.id,
        "institution_id": c.institution_id,
        "display_name": c.display_name,
        "kind": c.kind,
        "category": c.category,
        "person": c.person,
        "last_balance": c.last_balance,
        "last_synced_at": str(c.last_synced_at) if c.last_synced_at else None,
        "status": c.status,
        "last_error": c.last_error,
    }


@app.get("/api/connections")
def get_connections(db: Session = Depends(get_db)):
    conns = db.query(BankConnection).order_by(BankConnection.created_at).all()
    return [_serialize_conn(c) for c in conns]


@app.post("/api/connections")
def add_connection(data: dict, db: Session = Depends(get_db)):
    institution_id = data.get("institution_id")
    kind = data.get("kind")

    if kind == "scraped":
        info = SCRAPED_INSTITUTIONS.get(institution_id)
        if not info:
            raise HTTPException(400, "מוסד לא נתמך")
        if not vault.is_unlocked():
            raise HTTPException(423, "יש לפתוח את הכספת קודם")
        creds = data.get("credentials") or {}
        missing = [f for f in info["fields"] if not creds.get(f)]
        if missing:
            raise HTTPException(400, f"חסרים שדות: {', '.join(missing)}")
        conn = BankConnection(
            institution_id=institution_id,
            display_name=data.get("display_name") or info["name"],
            kind="scraped",
            category=info["category"],
            person=data.get("person", "משותף"),
            encrypted_credentials=vault.encrypt_credentials(creds),
            status="never",
        )
    elif kind == "manual":
        info = MANUAL_INSTITUTIONS.get(institution_id)
        if not info:
            raise HTTPException(400, "מוסד לא נתמך")
        conn = BankConnection(
            institution_id=institution_id,
            display_name=data.get("display_name") or info["name"],
            kind="manual",
            category=info["category"],
            person=data.get("person", "משותף"),
            last_balance=float(data.get("balance") or 0),
            status="ok",
            last_synced_at=datetime.utcnow(),
        )
    else:
        raise HTTPException(400, "kind לא תקין - scraped/manual בלבד")

    db.add(conn)
    db.commit()
    db.refresh(conn)

    if conn.kind == "manual":
        db.add(BalanceSnapshot(connection_id=conn.id, balance=conn.last_balance or 0))
        db.commit()
    record_networth_snapshot(db)

    return _serialize_conn(conn)


@app.put("/api/connections/{conn_id}/balance")
def update_manual_balance(conn_id: int, data: dict, db: Session = Depends(get_db)):
    conn = db.query(BankConnection).filter(BankConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(404, "לא נמצא")
    if conn.kind != "manual":
        raise HTTPException(400, "עדכון ידני אפשרי רק לחיבורים מסוג ידני")
    conn.last_balance = float(data["balance"])
    conn.last_synced_at = datetime.utcnow()
    conn.status = "ok"
    db.add(BalanceSnapshot(connection_id=conn.id, balance=conn.last_balance))
    db.commit()
    db.refresh(conn)
    record_networth_snapshot(db)
    return _serialize_conn(conn)


@app.post("/api/connections/{conn_id}/sync")
def sync_now(conn_id: int, db: Session = Depends(get_db)):
    conn = db.query(BankConnection).filter(BankConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(404, "לא נמצא")
    if conn.kind != "scraped":
        raise HTTPException(400, "לחיבור ידני אין סנכרון אוטומטי - עדכנו יתרה ידנית")
    if not vault.is_unlocked():
        raise HTTPException(423, "יש לפתוח את הכספת קודם")
    sync_connection(db, conn)
    db.refresh(conn)
    return _serialize_conn(conn)


@app.delete("/api/connections/{conn_id}")
def delete_connection(conn_id: int, db: Session = Depends(get_db)):
    conn = db.query(BankConnection).filter(BankConnection.id == conn_id).first()
    if not conn:
        raise HTTPException(404, "לא נמצא")
    db.query(BalanceSnapshot).filter(BalanceSnapshot.connection_id == conn_id).delete()
    db.delete(conn)
    db.commit()
    record_networth_snapshot(db)
    return {"ok": True}


# ─── הון כולל ──────────────────────────────────────────────────────────────────

@app.get("/api/networth")
def get_networth(db: Session = Depends(get_db)):
    conns = db.query(BankConnection).order_by(BankConnection.created_at).all()
    total = sum(c.last_balance or 0 for c in conns)

    by_category: dict[str, float] = {}
    for c in conns:
        cat = c.category or "other"
        by_category[cat] = by_category.get(cat, 0) + (c.last_balance or 0)

    history = db.query(NetWorthSnapshot).order_by(NetWorthSnapshot.day).all()

    return {
        "total": round(total, 2),
        "by_category": [{"category": k, "total": round(v, 2)} for k, v in by_category.items()],
        "connections": [_serialize_conn(c) for c in conns],
        "history": [{"day": h.day, "total": round(h.total, 2)} for h in history],
    }


# ─── Serve Frontend ───────────────────────────────────────────────────────────

if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
