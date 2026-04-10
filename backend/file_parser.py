import pandas as pd
import re
from datetime import datetime
from pathlib import Path

try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


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
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val
    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"]:
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except ValueError:
            continue
    return None


def parse_excel(filepath: str) -> list[dict]:
    rows = []
    xl = pd.ExcelFile(filepath)

    for sheet in xl.sheet_names:
        df = xl.parse(sheet, header=None)

        # Find header row - look for row with date-like and amount-like columns
        header_row = 0
        for i, row in df.iterrows():
            row_str = " ".join(str(v).lower() for v in row.values)
            if any(word in row_str for word in ["תאריך", "date", "סכום", "amount", "תיאור", "description", "פירוט"]):
                header_row = i
                break

        df = xl.parse(sheet, header=header_row)
        df.columns = [str(c).strip() for c in df.columns]

        # Map column names
        col_map = {}
        for col in df.columns:
            cl = col.lower()
            if any(w in cl for w in ["תאריך", "date"]):
                col_map["date"] = col
            elif any(w in cl for w in ["תיאור", "פירוט", "description", "שם", "name"]):
                col_map["description"] = col
            elif any(w in cl for w in ["סכום", "amount", "חיוב", "זכות", "credit", "debit"]):
                if "amount" not in col_map:
                    col_map["amount"] = col
            elif any(w in cl for w in ["קטגוריה", "category"]):
                col_map["category"] = col

        if "date" not in col_map or "amount" not in col_map:
            continue

        for _, row in df.iterrows():
            date = parse_date(row.get(col_map["date"]))
            if not date:
                continue
            try:
                amount = float(str(row[col_map["amount"]]).replace(",", "").replace("₪", "").strip())
            except (ValueError, TypeError):
                continue

            desc_col = col_map.get("description")
            description = str(row[desc_col]).strip() if desc_col else "לא ידוע"
            category = str(row[col_map["category"]]).strip() if "category" in col_map else guess_category(description)

            rows.append({
                "date": date.date(),
                "description": description,
                "amount": abs(amount),
                "category": category,
                "person": "משותף",
            })

    return rows


def parse_pdf(filepath: str) -> list[dict]:
    rows = []
    date_pattern = re.compile(r"\d{1,2}[./]\d{1,2}[./]\d{2,4}")
    amount_pattern = re.compile(r"[\d,]+\.\d{2}")

    with pdfplumber.open(filepath) as pdf:  # type: ignore
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row:
                        continue
                    row_text = " ".join(str(c) for c in row if c)
                    date_match = date_pattern.search(row_text)
                    amount_match = amount_pattern.search(row_text)
                    if not date_match or not amount_match:
                        continue
                    date = parse_date(date_match.group())
                    if not date:
                        continue
                    amount = float(amount_match.group().replace(",", ""))
                    description = row_text[:100]
                    rows.append({
                        "date": date.date(),
                        "description": description,
                        "amount": abs(amount),
                        "category": guess_category(description),
                        "person": "משותף",
                    })

    return rows


def parse_file(filepath: str) -> list[dict]:
    ext = Path(filepath).suffix.lower()
    if ext in [".xlsx", ".xls", ".csv"]:
        if ext == ".csv":
            df = pd.read_csv(filepath)
            # minimal CSV parsing
            rows = []
            for _, row in df.iterrows():
                rows.append({
                    "date": datetime.today().date(),
                    "description": str(row.iloc[0]),
                    "amount": abs(float(str(row.iloc[-1]).replace(",", ""))),
                    "category": "כללי",
                    "person": "משותף",
                })
            return rows
        return parse_excel(filepath)
    elif ext == ".pdf":
        if not HAS_PDF:
            raise ValueError("ייבוא PDF אינו נתמך. אנא השתמש בקבצי Excel או CSV.")
        return parse_pdf(filepath)
    return []
