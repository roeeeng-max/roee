import csv
import re
from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook


CATEGORY_KEYWORDS = {
    "סופרמרקט": ["רמי לוי", "שופרסל", "מגה", "יינות", "סיטי", "סופר", "מכולת", "victory", "fresh"],
    "דלק": ["דלק", "סונול", "פז", "תן", "fuel", "gas"],
    "מסעדות": ["מקדונלד", "בורגר", "פיצה", "שווארמה", "סושי", "מסעדה", "cafe", "קפה", "coffee", "wolt", "10bis"],
    "בריאות": ["קופת חולים", "מכבי", "כללית", "ביטוח", "רופא", "תרופה", "pharmacy", "super-pharm"],
    "ביגוד": ["זארה", "H&M", "מנגו", "ASOS", "ביגוד", "נעליים", "next"],
    "בידור": ["netflix", "spotify", "youtube", "סרט", "קולנוע", "theatre"],
    "חינוך": ["בית ספר", "גן", "שכר לימוד", "ספרים", "קורס"],
    "תחבורה": ["אגד", "דן", "רב-קו", "מונית", "uber", "gett", "תחבורה"],
    "חשמל/מים": ["חשמל", "מים", "גז", "ועד בית", "ארנונה"],
    "תקשורת": ["סלקום", "פרטנר", "hot", "yes", "bezeq", "בזק"],
}


def guess_category(description: str) -> str:
    desc_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in desc_lower:
                return category
    return "כללי"


def parse_date(val) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except ValueError:
            continue
    return None


def parse_amount(val) -> float | None:
    if val is None:
        return None
    try:
        return abs(float(str(val).replace(",", "").replace("₪", "").strip()))
    except (ValueError, TypeError):
        return None


def parse_excel(filepath: str) -> list[dict]:
    wb = load_workbook(filepath, data_only=True)
    rows = []

    for ws in wb.worksheets:
        all_rows = list(ws.iter_rows(values_only=True))
        if not all_rows:
            continue

        # Find header row
        header_row_idx = 0
        for i, row in enumerate(all_rows):
            row_str = " ".join(str(v).lower() for v in row if v is not None)
            if any(w in row_str for w in ["תאריך", "date", "סכום", "amount", "תיאור", "פירוט"]):
                header_row_idx = i
                break

        headers = [str(h).strip() if h is not None else "" for h in all_rows[header_row_idx]]

        # Map columns
        col_date = col_desc = col_amount = col_cat = None
        for i, h in enumerate(headers):
            hl = h.lower()
            if any(w in hl for w in ["תאריך", "date"]):
                col_date = i
            elif any(w in hl for w in ["תיאור", "פירוט", "description", "שם"]):
                col_desc = i
            elif any(w in hl for w in ["סכום", "amount", "חיוב", "זכות"]):
                if col_amount is None:
                    col_amount = i
            elif any(w in hl for w in ["קטגוריה", "category"]):
                col_cat = i

        if col_date is None or col_amount is None:
            continue

        for row in all_rows[header_row_idx + 1:]:
            if len(row) <= max(filter(None, [col_date, col_amount])):
                continue
            date = parse_date(row[col_date])
            if not date:
                continue
            amount = parse_amount(row[col_amount])
            if amount is None:
                continue
            description = str(row[col_desc]).strip() if col_desc is not None and row[col_desc] else "לא ידוע"
            category = str(row[col_cat]).strip() if col_cat is not None and row[col_cat] else guess_category(description)

            rows.append({
                "date": date.date(),
                "description": description,
                "amount": amount,
                "category": category,
                "person": "משותף",
            })

    return rows


def parse_csv(filepath: str) -> list[dict]:
    rows = []
    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []

        col_date = col_desc = col_amount = None
        for h in headers:
            hl = h.lower()
            if any(w in hl for w in ["תאריך", "date"]):
                col_date = h
            elif any(w in hl for w in ["תיאור", "פירוט", "description", "שם"]):
                col_desc = h
            elif any(w in hl for w in ["סכום", "amount", "חיוב"]):
                if col_amount is None:
                    col_amount = h

        for row in reader:
            date = parse_date(row.get(col_date or "")) if col_date else datetime.today()
            if not date:
                continue
            raw_amount = row.get(col_amount or "", "0") if col_amount else list(row.values())[-1]
            amount = parse_amount(raw_amount)
            if amount is None:
                continue
            description = row.get(col_desc or "", "לא ידוע") if col_desc else list(row.values())[0]
            rows.append({
                "date": date.date() if hasattr(date, "date") else date,
                "description": str(description).strip(),
                "amount": amount,
                "category": guess_category(str(description)),
                "person": "משותף",
            })
    return rows


def parse_file(filepath: str) -> list[dict]:
    ext = Path(filepath).suffix.lower()
    if ext in [".xlsx", ".xls"]:
        return parse_excel(filepath)
    elif ext == ".csv":
        return parse_csv(filepath)
    elif ext == ".pdf":
        raise ValueError("ייבוא PDF אינו נתמך כרגע. אנא השתמש בקבצי Excel או CSV.")
    return []
