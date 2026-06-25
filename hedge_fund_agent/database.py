import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "hedge_fund_data.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS fund_filings (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                fund_cik         TEXT NOT NULL,
                fund_name        TEXT NOT NULL,
                accession_number TEXT NOT NULL UNIQUE,
                period_of_report TEXT,
                filed_date       TEXT,
                processed_at     TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS fund_positions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                filing_id       INTEGER NOT NULL,
                fund_cik        TEXT NOT NULL,
                period          TEXT NOT NULL,
                cusip           TEXT NOT NULL,
                issuer_name     TEXT NOT NULL,
                value_thousands INTEGER NOT NULL DEFAULT 0,
                shares          INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_pos_fund_period
                ON fund_positions(fund_cik, period);
            CREATE INDEX IF NOT EXISTS idx_pos_cusip
                ON fund_positions(fund_cik, cusip, period);

            CREATE TABLE IF NOT EXISTS ma_events (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                company_cik      TEXT NOT NULL,
                company_name     TEXT NOT NULL,
                form_type        TEXT NOT NULL,
                accession_number TEXT NOT NULL UNIQUE,
                filed_date       TEXT NOT NULL,
                description      TEXT,
                filing_url       TEXT,
                notified         INTEGER DEFAULT 0
            );
        """)


# ── Fund filings ──────────────────────────────────────────────────────────────

def filing_exists(conn: sqlite3.Connection, accession: str) -> bool:
    row = conn.execute(
        "SELECT id FROM fund_filings WHERE accession_number = ?", (accession,)
    ).fetchone()
    return row is not None


def save_filing(conn: sqlite3.Connection, cik: str, name: str, filing: dict) -> int:
    cur = conn.execute(
        """INSERT INTO fund_filings
               (fund_cik, fund_name, accession_number, period_of_report, filed_date)
           VALUES (?, ?, ?, ?, ?)""",
        (cik, name, filing["accession"], filing["period"], filing["filed_date"]),
    )
    conn.commit()
    return cur.lastrowid


def save_positions(
    conn: sqlite3.Connection,
    filing_id: int,
    cik: str,
    period: str,
    holdings: list[dict],
):
    conn.executemany(
        """INSERT INTO fund_positions
               (filing_id, fund_cik, period, cusip, issuer_name, value_thousands, shares)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [
            (filing_id, cik, period, h["cusip"], h["issuer"], h["value"], h["shares"])
            for h in holdings
        ],
    )
    conn.commit()


def get_positions_for_period(
    conn: sqlite3.Connection, cik: str, period: str
) -> list[dict]:
    rows = conn.execute(
        """SELECT cusip,
                  issuer_name AS issuer,
                  value_thousands AS value,
                  shares
           FROM fund_positions
           WHERE fund_cik = ? AND period = ?""",
        (cik, period),
    ).fetchall()
    return [dict(r) for r in rows]


def get_prev_period(
    conn: sqlite3.Connection, cik: str, current_period: str
) -> Optional[str]:
    """Return the most-recent period before current_period that we have data for."""
    row = conn.execute(
        """SELECT period_of_report
           FROM fund_filings
           WHERE fund_cik = ? AND period_of_report < ?
           ORDER BY period_of_report DESC
           LIMIT 1""",
        (cik, current_period),
    ).fetchone()
    return row["period_of_report"] if row else None


# ── M&A events ────────────────────────────────────────────────────────────────

def save_ma_event(
    conn: sqlite3.Connection, cik: str, name: str, filing: dict
) -> bool:
    """Insert a new M&A event. Returns True if it was new (not already stored)."""
    if conn.execute(
        "SELECT id FROM ma_events WHERE accession_number = ?", (filing["accession"],)
    ).fetchone():
        return False

    conn.execute(
        """INSERT INTO ma_events
               (company_cik, company_name, form_type, accession_number,
                filed_date, description, filing_url)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            cik,
            name,
            filing["form"],
            filing["accession"],
            filing["filed_date"],
            filing.get("description", ""),
            filing.get("url", ""),
        ),
    )
    conn.commit()
    return True


def get_unnotified_ma_events(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM ma_events WHERE notified = 0 ORDER BY filed_date DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def mark_ma_events_notified(conn: sqlite3.Connection):
    conn.execute("UPDATE ma_events SET notified = 1 WHERE notified = 0")
    conn.commit()
