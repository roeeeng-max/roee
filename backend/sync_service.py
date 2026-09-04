# לוגיקת הסנכרון המשותפת - גם ל"סנכרן עכשיו" הידני מהממשק וגם לג'וב היומי
# האוטומטי (ראו scheduler.py).
from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

import scraper_bridge
import vault
from models import BalanceSnapshot, BankConnection, NetWorthSnapshot


def compute_balance(category: str, result: dict) -> float:
    """מחשב יתרה כוללת מתוך תוצאת הסקרייפר. חשבון בנק נספר כנכס (+),
    כרטיס אשראי נספר כהתחייבות (-) - סכום שעדיין ייגבה מהחשבון."""
    accounts = result.get("accounts") or []
    total = 0.0
    for acc in accounts:
        balance = acc.get("balance")
        if category == "credit_card":
            if balance is not None:
                total -= balance
            else:
                txns = acc.get("txns") or []
                total -= sum(t.get("chargedAmount") or 0 for t in txns)
        else:
            total += balance or 0
    return total


def record_networth_snapshot(db: Session) -> None:
    today = date.today().isoformat()
    total = db.query(func.sum(BankConnection.last_balance)).scalar() or 0
    row = db.query(NetWorthSnapshot).filter(NetWorthSnapshot.day == today).first()
    if row:
        row.total = total
    else:
        db.add(NetWorthSnapshot(day=today, total=total))
    db.commit()


def sync_connection(db: Session, conn: BankConnection) -> None:
    """מסנכרן חיבור scraped יחיד: מפענח את הפרטים מהכספת, מריץ את הסקרייפר
    ומעדכן יתרה/סטטוס. לא עושה כלום לחיבורים מסוג manual."""
    if conn.kind != "scraped":
        return

    if not vault.is_unlocked():
        conn.status = "locked"
        conn.last_error = "הכספת נעולה - יש לפתוח אותה כדי לסנכרן"
        db.commit()
        return

    try:
        credentials = vault.decrypt_credentials(conn.encrypted_credentials)
    except Exception:
        conn.status = "error"
        conn.last_error = "שגיאת פענוח פרטי ההתחברות - נסו לפתוח את הכספת מחדש"
        db.commit()
        return

    try:
        result = scraper_bridge.run_scrape(conn.institution_id, credentials)
    except scraper_bridge.ScraperUnavailable as exc:
        conn.status = "error"
        conn.last_error = str(exc)
        db.commit()
        return

    if result.get("success"):
        balance = compute_balance(conn.category, result)
        conn.last_balance = balance
        conn.status = "ok"
        conn.last_error = None
        conn.last_synced_at = datetime.utcnow()
        db.add(BalanceSnapshot(connection_id=conn.id, balance=balance))
    else:
        conn.status = "error"
        conn.last_error = result.get("errorMessage") or result.get("errorType") or "שגיאה לא ידועה בסנכרון"

    db.commit()
    record_networth_snapshot(db)
