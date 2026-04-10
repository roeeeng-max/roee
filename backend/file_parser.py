import csv
import re
from datetime import datetime
from pathlib import Path
from openpyxl import load_workbook


CATEGORY_KEYWORDS = {
    "סופרמרקט": ["רמי לוי", "שופרסל", "מגה", "יינות", "סיטי", "סופר", "מכולת", "victory", "fresh", "מזון", "צרכנייה"],
    "דלק": ["דלק", "סונול", "פז", "תן", "fuel", "gas"],
    "מסעדות": ["מקדונלד", "בורגר", "פיצה", "שווארמה", "סושי", "מסעדה", "cafe", "קפה", "coffee", "wolt", "10bis", "אוכל בחוץ"],
    "בריאות": ["קופת חולים", "מכבי", "כללית", "ביטוח", "רופא", "תרופה", "pharmacy", "super-pharm", "בריאות"],
    "ביגוד": ["זארה", "H&M", "מנגו", "ASOS", "ביגוד", "נעליים", "next", "הלבשה"],
    "בידור": ["netflix", "spotify", "youtube", "סרט", "קולנוע", "theatre", "בידור", "פנאי"],
    "חינוך": ["בית ספר", "גן", "שכר לימוד", "ספרים", "קורס", "חינוך"],
    "תחבורה": ["אגד", "דן", "רב-קו", "מונית", "uber", "gett", "תחבורה", "רכב", "חניה", "סלקום רכב"],
    "חשמל/מים": ["חשמל", "מים", "גז", "ועד בית", "ארנונה"],
    "תקשורת": ["סלקום", "פרטנר", "hot", "yes", "bezeq", "בזק", "תקשורת"],
    "קניות": ["אמזון", "amazon", "ebay", "אלי אקספרס", "קניות"],
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
        cleaned = str(val).replace(",", "").replace("₪", "").replace(" ", "").strip()
        if not cleaned or cleaned in ["-", "—", ""]:
            return None
        return abs(float(cleaned))
    except (ValueError, TypeError):
        return None


def try_parse_financial_report(all_rows: list) -> list[dict]:
    """
    מפרסר דוחות פיננסיים בפורמט: שם בית העסק | FY23 | FY24 | FY25 | LTM-...
    """
    # מחפש את העמודה עם "שם בית העסק"
    name_col = None
    name_row_idx = None

    for i, row in enumerate(all_rows):
        for j, cell in enumerate(row):
            if cell and "שם בית העסק" in str(cell):
                name_col = j
                name_row_idx = i
                break
        if name_col is not None:
            break

    if name_col is None:
        return []

    # מחפש עמודות לפי שנה בשורות הכותרת
    PERIODS = {
        "LTM-Feb26": 2026, "LTM-Feb 26": 2026, "LTM Feb26": 2026,
        "LTM-Sep23": 2023, "LTM Sep23": 2023,
        "FY25": 2025, "FY24": 2024, "FY23": 2023, "FY22": 2022,
    }

    period_cols = {}  # {period_name: col_index}
    period_years = {}  # {period_name: year}

    search_start = max(0, name_row_idx - 4)
    search_end = min(len(all_rows), name_row_idx + 2)

    for i in range(search_start, search_end):
        for j, cell in enumerate(all_rows[i]):
            if not cell:
                continue
            cell_str = str(cell).strip()
            for period, year in PERIODS.items():
                if period.lower() in cell_str.lower() and period not in period_cols:
                    period_cols[period] = j
                    period_years[period] = year

    if not period_cols:
        return []

    # סדר עדיפויות - הכי עדכני קודם
    preferred_order = [
        "LTM-Feb26", "LTM-Feb 26", "LTM Feb26",
        "FY25", "FY24", "FY23", "FY22",
        "LTM-Sep23", "LTM Sep23"
    ]

    rows_out = []

    for row in all_rows[name_row_idx + 1:]:
        if not row or len(row) <= name_col:
            continue

        name = row[name_col]
        if not name:
            continue
        name_str = str(name).strip()
        if not name_str or name_str in ["None", ""]:
            continue
        # דלג על שורות סיכום
        if any(x in name_str for x in ['סה"כ', "סך הכל", "Total", "TOTAL", "סה''כ"]):
            continue

        # ייבא נתונים לכל שנה זמינה
        imported_for_business = False
        for period in preferred_order:
            if period not in period_cols:
                continue
            col_j = period_cols[period]
            if col_j >= len(row):
                continue

            amount = parse_amount(row[col_j])
            if not amount or amount <= 0:
                continue

            year = period_years[period]
            rows_out.append({
                "date": datetime(year, 6, 15).date(),
                "description": name_str,
                "amount": amount,
                "category": guess_category(name_str),
                "person": "משותף",
            })
            imported_for_business = True

        # אם לא מצאנו כלום בסדר העדיפויות - נסה כל עמודה
        if not imported_for_business:
            for period, col_j in period_cols.items():
                if col_j >= len(row):
                    continue
                amount = parse_amount(row[col_j])
                if amount and amount > 0:
                    year = period_years[period]
                    rows_out.append({
                        "date": datetime(year, 6, 15).date(),
                        "description": name_str,
                        "amount": amount,
                        "category": guess_category(name_str),
                        "person": "משותף",
                    })

    return rows_out


def parse_excel(filepath: str) -> list[dict]:
    wb = load_workbook(filepath, data_only=True)
    rows = []

    for ws in wb.worksheets:
        all_rows = list(ws.iter_rows(values_only=True))
        if not all_rows:
            continue

        # נסה פורמט דוח פיננסי (FY/LTM עמודות)
        report_rows = try_parse_financial_report(all_rows)
        if report_rows:
            rows.extend(report_rows)
            continue

        # פורמט עסקאות רגיל - חפש כותרת
        header_row_idx = 0
        for i, row in enumerate(all_rows):
            row_str = " ".join(str(v).lower() for v in row if v is not None)
            if any(word in row_str for word in ["תאריך", "date", "סכום", "amount", "תיאור", "פירוט"]):
                header_row_idx = i
                break

        headers = [str(h).strip() if h is not None else "" for h in all_rows[header_row_idx]]

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
            if not row:
                continue
            max_col = max(c for c in [col_date, col_amount] if c is not None)
            if len(row) <= max_col:
                continue
            date = parse_date(row[col_date])
            if not date:
                continue
            amount = parse_amount(row[col_amount])
            if amount is None:
                continue
            description = str(row[col_desc]).strip() if col_desc is not None and col_desc < len(row) and row[col_desc] else "לא ידוע"
            category = str(row[col_cat]).strip() if col_cat is not None and col_cat < len(row) and row[col_cat] else guess_category(description)

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
