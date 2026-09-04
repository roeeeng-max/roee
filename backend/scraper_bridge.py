# מפעיל את שירות ה-Node שבתיקיית scraper/ כתהליך צאצא, ומתקשר איתו דרך
# stdin/stdout ב-JSON. ראו scraper/scrape.js ו-scraper/README.md.
import json
import os
import subprocess
from shutil import which

SCRAPER_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scraper"))
SCRAPER_TIMEOUT_SECONDS = 180


class ScraperUnavailable(Exception):
    """נזרקת כשאי אפשר בכלל לנסות להריץ את הסקרייפר (Node/חבילות חסרים)."""


def is_node_available() -> bool:
    return which("node") is not None


def is_scraper_ready() -> bool:
    return is_node_available() and os.path.isdir(os.path.join(SCRAPER_DIR, "node_modules"))


def run_scrape(institution_id: str, credentials: dict, months_back: int = 2) -> dict:
    if not is_node_available():
        raise ScraperUnavailable(
            "Node.js לא נמצא במחשב - חיבור אוטומטי לבנקים דורש התקנת Node.js (ראו scraper/README.md)"
        )
    if not os.path.isdir(os.path.join(SCRAPER_DIR, "node_modules")):
        raise ScraperUnavailable(
            "חבילות ה-scraper לא הותקנו - יש להריץ 'npm install' בתוך תיקיית scraper (ראו scraper/README.md)"
        )

    payload = json.dumps({
        "companyId": institution_id,
        "credentials": credentials,
        "monthsBack": months_back,
    })

    try:
        proc = subprocess.run(
            ["node", "scrape.js"],
            input=payload,
            cwd=SCRAPER_DIR,
            capture_output=True,
            text=True,
            timeout=SCRAPER_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "errorType": "TIMEOUT", "errorMessage": "פג הזמן הקצוב להתחברות לגוף הפיננסי"}

    lines = [l for l in proc.stdout.splitlines() if l.strip()]
    if not lines:
        detail = (proc.stderr or "לא התקבלה תגובה מהסקרייפר").strip()[-2000:]
        return {"success": False, "errorType": "NO_OUTPUT", "errorMessage": detail}

    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        detail = (proc.stdout + "\n" + proc.stderr).strip()[-2000:]
        return {"success": False, "errorType": "PARSE_ERROR", "errorMessage": detail}
