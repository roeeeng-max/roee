"""
Utility: search SEC EDGAR for a company's CIK number.

Usage:
    python find_cik.py "Citadel Advisors"
    python find_cik.py "Renaissance Technologies"
"""

import sys
import time
import requests

HEADERS = {"User-Agent": "HedgeFundMonitor roeeeng@gmail.com"}


def search_edgar(name: str) -> list[dict]:
    """Search EDGAR full-text search for 13F filers matching `name`."""
    url = (
        "https://efts.sec.gov/LATEST/search-index"
        f"?q=%22{requests.utils.quote(name)}%22&forms=13F-HR&hits.hits._source=entity_name,file_num,period_of_report"
    )
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(0.2)

    seen:    set[str] = set()
    results: list[dict] = []

    for hit in resp.json().get("hits", {}).get("hits", [])[:20]:
        src    = hit.get("_source", {})
        entity = src.get("entity_name", "").strip()
        # Extract CIK from _id (format: "cik_accession")
        doc_id = hit.get("_id", "")
        cik    = doc_id.split("_")[0] if "_" in doc_id else ""

        if entity and entity not in seen:
            seen.add(entity)
            results.append({"name": entity, "cik": cik})

    return results


def get_cik_by_name(name: str) -> list[dict]:
    """Alternative: use the EDGAR company-name search endpoint."""
    url  = f"https://www.sec.gov/cgi-bin/browse-edgar?company={requests.utils.quote(name)}&CIK=&type=13F-HR&action=getcompany&output=atom"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    time.sleep(0.2)

    # Parse Atom XML
    import xml.etree.ElementTree as ET
    ns   = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(resp.text)

    results: list[dict] = []
    seen: set[str] = set()
    for entry in root.findall("a:entry", ns):
        cik_el   = entry.find("a:id", ns)
        name_el  = entry.find("a:company-name", ns)
        if cik_el is None or name_el is None:
            continue
        # id looks like https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001423053...
        cik_url  = cik_el.text or ""
        cik_part = ""
        if "CIK=" in cik_url:
            cik_part = cik_url.split("CIK=")[1].split("&")[0].lstrip("0")
        entity = name_el.text or ""
        if entity and entity not in seen:
            seen.add(entity)
            results.append({"name": entity, "cik": cik_part})

    return results


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Citadel Advisors"
    print(f"\nSearching EDGAR for: {query}\n")

    results = get_cik_by_name(query)
    if not results:
        results = search_edgar(query)

    if not results:
        print("No results found.")
    else:
        print(f"{'Company Name':<55} CIK")
        print("-" * 70)
        for r in results[:15]:
            print(f"  {r['name']:<53} {r['cik']}")
    print()
