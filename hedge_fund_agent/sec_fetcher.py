"""
SEC EDGAR API client.

Rate limit: 10 req/sec. We sleep 0.15 s between calls to stay safe.
User-Agent header is required by SEC policy.
"""

import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from config import SEC_USER_AGENT, MA_FORM_TYPES

_HEADERS = {
    "User-Agent": SEC_USER_AGENT,
    "Accept-Encoding": "gzip, deflate",
}

EDGAR_DATA = "https://data.sec.gov"
SEC        = "https://www.sec.gov"


def _get(url: str, **kw) -> requests.Response:
    resp = requests.get(url, headers=_HEADERS, timeout=30, **kw)
    resp.raise_for_status()
    time.sleep(0.15)
    return resp


# ── Submissions ───────────────────────────────────────────────────────────────

def get_submissions(cik: str) -> dict:
    padded = cik.zfill(10)
    return _get(f"{EDGAR_DATA}/submissions/CIK{padded}.json").json()


def get_recent_filings(cik: str, form_types: list[str], days: int = 90) -> list[dict]:
    """Return filings matching form_types filed within the last `days` days."""
    data    = get_submissions(cik)
    recent  = data.get("filings", {}).get("recent", {})
    cutoff  = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    forms       = recent.get("form", [])
    accessions  = recent.get("accessionNumber", [])
    dates       = recent.get("filingDate", [])
    periods     = recent.get("reportDate", [])
    docs        = recent.get("primaryDocument", [])

    results = []
    for i, form in enumerate(forms):
        if form not in form_types:
            continue
        filed = dates[i] if i < len(dates) else ""
        if filed < cutoff:
            continue
        acc = accessions[i] if i < len(accessions) else ""
        results.append(
            {
                "form":        form,
                "accession":   acc,
                "filed_date":  filed,
                "period":      periods[i] if i < len(periods) else "",
                "description": docs[i]    if i < len(docs)    else "",
                "url": (
                    f"{SEC}/Archives/edgar/data/{cik}/"
                    f"{acc.replace('-', '')}/"
                )
                if acc
                else "",
            }
        )
    return results


# ── 13F Holdings ──────────────────────────────────────────────────────────────

def get_13f_holdings(cik: str, accession: str) -> list[dict]:
    """Download and parse the information-table XML from a 13F-HR filing."""
    acc_clean = accession.replace("-", "")
    index_url = f"{SEC}/Archives/edgar/data/{cik}/{acc_clean}/index.json"

    try:
        index = _get(index_url).json()
    except Exception:
        return []

    xml_filename = _find_infotable_filename(index)
    if not xml_filename:
        return []

    xml_url = f"{SEC}/Archives/edgar/data/{cik}/{acc_clean}/{xml_filename}"
    try:
        xml_text = _get(xml_url).text
    except Exception:
        return []

    return _parse_13f_xml(xml_text)


def _find_infotable_filename(index: dict) -> str | None:
    items = index.get("directory", {}).get("item", [])
    # Prefer files whose name contains "infotable"
    for item in items:
        name = item.get("name", "")
        if "infotable" in name.lower() and name.endswith(".xml"):
            return name
    # Fall back to any non-header XML
    for item in items:
        name = item.get("name", "")
        if name.endswith(".xml") and "header" not in name.lower():
            return name
    return None


def _parse_13f_xml(xml_text: str) -> list[dict]:
    # Strip namespace declarations so ElementTree works with plain tag names
    clean = re.sub(r'\s+xmlns(?::\w+)?="[^"]*"', "", xml_text)
    try:
        root = ET.fromstring(clean)
    except ET.ParseError:
        return []

    def txt(el, tag: str) -> str:
        node = el.find(tag)
        return node.text.strip() if node is not None and node.text else ""

    holdings = []
    for entry in root.iter("infoTable"):
        val_str    = txt(entry, "value").replace(",", "")
        shares_el  = entry.find(".//sshPrnamt")

        try:
            value = int(val_str)
        except ValueError:
            value = 0

        try:
            shares = int(shares_el.text.replace(",", "")) if shares_el is not None and shares_el.text else 0
        except ValueError:
            shares = 0

        if value <= 0:
            continue

        holdings.append(
            {
                "issuer": txt(entry, "nameOfIssuer"),
                "cusip":  txt(entry, "cusip"),
                "title":  txt(entry, "titleOfClass"),
                "value":  value,   # thousands USD
                "shares": shares,
            }
        )

    holdings.sort(key=lambda h: h["value"], reverse=True)
    return holdings


# ── M&A / Acquisition filings ─────────────────────────────────────────────────

def get_ma_filings(cik: str, days: int = 1) -> list[dict]:
    """Return SC-TO / SC-13D acquisition filings filed in the last `days` days."""
    return get_recent_filings(cik, MA_FORM_TYPES, days=days)
