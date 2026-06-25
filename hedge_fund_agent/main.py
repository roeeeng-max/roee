"""
Hedge-fund daily monitor.

Usage:
    python main.py           # Start scheduler (runs every day at DAILY_RUN_TIME)
    python main.py --once    # Run once now and exit (useful for testing / cron)
    python main.py --dry     # --once but don't send email (print only)
"""

import logging
import sys
import os

# Allow running as  python hedge_fund_agent/main.py  from the project root
sys.path.insert(0, os.path.dirname(__file__))

import schedule
import time

from config import (
    HEDGE_FUNDS, LARGE_COMPANIES,
    MIN_POSITION_VALUE_K, MIN_CHANGE_PCT,
    DAILY_RUN_TIME, SEND_IF_NO_NEWS,
)
from database import (
    init_db, get_conn,
    filing_exists, save_filing, save_positions,
    get_positions_for_period, get_prev_period,
    save_ma_event, get_unnotified_ma_events, mark_ma_events_notified,
)
from sec_fetcher import get_recent_filings, get_13f_holdings, get_ma_filings
from analyzer import analyze_changes
from formatter import build_messages, no_news_message
from email_sender import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DRY_RUN = "--dry" in sys.argv


# ── Core logic ────────────────────────────────────────────────────────────────

def check_hedge_funds() -> list[dict]:
    """Fetch and analyze new 13F filings. Returns list of fund-update dicts."""
    updates = []

    for fund in HEDGE_FUNDS:
        try:
            log.info(f"Checking {fund['name']} …")
            filings = get_recent_filings(fund["cik"], ["13F-HR", "13F-HR/A"], days=90)

            if not filings:
                log.info(f"  No recent 13F filings found.")
                continue

            filing = filings[0]  # Most recent

            with get_conn() as conn:
                if filing_exists(conn, filing["accession"]):
                    log.info(f"  Already processed: {filing['accession']}")
                    continue

            log.info(f"  New filing: {filing['accession']} (period: {filing['period']})")
            holdings = get_13f_holdings(fund["cik"], filing["accession"])
            log.info(f"  Parsed {len(holdings)} holdings")

            if not holdings:
                continue

            with get_conn() as conn:
                prev_period = get_prev_period(conn, fund["cik"], filing["period"])
                prev_holdings = (
                    get_positions_for_period(conn, fund["cik"], prev_period)
                    if prev_period
                    else []
                )

            changes = analyze_changes(
                holdings, prev_holdings, MIN_POSITION_VALUE_K, MIN_CHANGE_PCT
            )
            log.info(f"  {len(changes)} significant changes (prev period: {prev_period or 'none'})")

            with get_conn() as conn:
                fid = save_filing(conn, fund["cik"], fund["name"], filing)
                save_positions(conn, fid, fund["cik"], filing["period"], holdings)

            if changes:
                updates.append(
                    {
                        "name":        fund["name"],
                        "period":      filing["period"],
                        "filed_date":  filing["filed_date"],
                        "changes":     changes,
                    }
                )

        except Exception as exc:
            log.error(f"Error processing {fund['name']}: {exc}", exc_info=True)

    return updates


def check_ma_activity() -> list[dict]:
    """Fetch new M&A / acquisition filings from large companies."""
    new_events = []

    for company in LARGE_COMPANIES:
        try:
            filings = get_ma_filings(company["cik"], days=2)
            with get_conn() as conn:
                for f in filings:
                    if save_ma_event(conn, company["cik"], company["name"], f):
                        log.info(f"  New M&A filing: {company['name']} {f['form']} ({f['filed_date']})")
        except Exception as exc:
            log.error(f"Error checking M&A for {company['name']}: {exc}", exc_info=True)

    with get_conn() as conn:
        rows = get_unnotified_ma_events(conn)
        for r in rows:
            new_events.append(
                {
                    "company":     r["company_name"],
                    "form":        r["form_type"],
                    "filed_date":  r["filed_date"],
                    "filing_url":  r.get("filing_url", ""),
                }
            )
        if new_events:
            mark_ma_events_notified(conn)

    return new_events


# ── Daily job ─────────────────────────────────────────────────────────────────

def run_daily_check():
    log.info("=" * 60)
    log.info("Daily hedge-fund check started")
    log.info("=" * 60)

    fund_updates = check_hedge_funds()
    ma_events    = check_ma_activity()

    messages = build_messages(fund_updates, ma_events)

    if not messages and SEND_IF_NO_NEWS:
        messages = [no_news_message()]

    if messages:
        if DRY_RUN:
            log.info("[DRY RUN] Would send %d email(s):", len(messages))
            for i, m in enumerate(messages, 1):
                print(f"\n─── Message {i} ───\n{m}")
        else:
            send_email(messages)
    else:
        log.info("Nothing to report today.")

    log.info("Daily check complete.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    init_db()
    log.info("Database initialised at hedge_fund_data.db")

    if "--once" in sys.argv or "--dry" in sys.argv:
        run_daily_check()
        return

    log.info(f"Scheduler started — will run every day at {DAILY_RUN_TIME}")
    schedule.every().day.at(DAILY_RUN_TIME).do(run_daily_check)

    # Run immediately on first startup so we don't wait until tomorrow
    log.info("Running initial check now …")
    run_daily_check()

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
