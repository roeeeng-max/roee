import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── Email (Gmail) ─────────────────────────────────────────────────────────────
GMAIL_USER         = os.getenv("GMAIL_USER", "")           # roeeeng@gmail.com
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")   # 16-char App Password
EMAIL_TO           = os.getenv("EMAIL_TO", "roeeeng@gmail.com")

# ── Scheduler ─────────────────────────────────────────────────────────────────
DAILY_RUN_TIME   = os.getenv("DAILY_RUN_TIME", "08:00")   # Israel time (UTC+3)
SEND_IF_NO_NEWS  = os.getenv("SEND_IF_NO_NEWS", "false").lower() == "true"

# ── SEC EDGAR ─────────────────────────────────────────────────────────────────
SEC_USER_AGENT = os.getenv("SEC_USER_AGENT", "HedgeFundMonitor roeeeng@gmail.com")

# ── Thresholds ────────────────────────────────────────────────────────────────
MIN_POSITION_VALUE_K = int(os.getenv("MIN_POSITION_VALUE", "5000"))   # $5M minimum
MIN_CHANGE_PCT       = float(os.getenv("MIN_CHANGE_PCT", "20.0"))     # 20% change

# ── Top 10 Hedge Funds (SEC 13F filers) ───────────────────────────────────────
# Run:  python find_cik.py "Fund Name"  to verify / update CIKs
HEDGE_FUNDS = [
    {"name": "Bridgewater Associates",    "cik": "1350694"},
    {"name": "Renaissance Technologies",  "cik": "1037389"},
    {"name": "Citadel Advisors",          "cik": "1423053"},
    {"name": "Millennium Management",     "cik": "1273087"},
    {"name": "D.E. Shaw",                 "cik": "1009207"},
    {"name": "Two Sigma Investments",     "cik": "1471009"},
    {"name": "AQR Capital Management",    "cik": "1135927"},
    {"name": "Point72 Asset Management",  "cik": "1603466"},
    {"name": "Balyasny Asset Management", "cik": "1454512"},
    {"name": "Viking Global Investors",   "cik": "1350752"},
]

# ── Large Companies – track SC-TO (tender offers) and 13D/G acquisitions ──────
LARGE_COMPANIES = [
    {"name": "Nvidia",            "cik": "1045810"},
    {"name": "Apple",             "cik": "320193"},
    {"name": "Microsoft",         "cik": "789019"},
    {"name": "Alphabet",          "cik": "1652044"},
    {"name": "Amazon",            "cik": "1018724"},
    {"name": "Meta",              "cik": "1326801"},
    {"name": "Tesla",             "cik": "1318605"},
    {"name": "Berkshire Hathaway","cik": "1067983"},
    {"name": "JPMorgan Chase",    "cik": "19617"},
    {"name": "Salesforce",        "cik": "1108524"},
]

# M&A / acquisition form types to watch
MA_FORM_TYPES = ["SC TO-T", "SC TO-C", "SC TO-I", "SC-TO-T", "SC-TO-C", "SC 13D", "SC 13D/A"]
