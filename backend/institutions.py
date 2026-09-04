# רשימת הגופים הפיננסיים הנתמכים.
#
# SCRAPED - גופים שהספרייה הפתוחה israeli-bank-scrapers יודעת "להתחבר" אליהם
# באופן אוטומטי (בדיוק כמו כניסה רגילה דרך הדפדפן) ולקרוא יתרה/תנועות.
# https://github.com/eshaham/israeli-bank-scrapers
#
# MANUAL - בתי השקעות/קרנות/חברות ביטוח ופנסיה שאין להם היום סקרייפר פתוח
# ואמין - היתרה שלהם מוזנת ידנית (למשל אחרי כניסה לאתר שלהם או למסלקה
# הפנסיונית) ומוצגת יחד עם כל השאר בתמונת ההון הכוללת.

SCRAPED_INSTITUTIONS = {
    "hapoalim":         {"name": "בנק הפועלים",        "category": "bank",        "fields": ["userCode", "password"]},
    "leumi":            {"name": "בנק לאומי",           "category": "bank",        "fields": ["username", "password"]},
    "discount":         {"name": "בנק דיסקונט",         "category": "bank",        "fields": ["id", "password", "num"]},
    "mercantile":       {"name": "בנק מרכנתיל",         "category": "bank",        "fields": ["id", "password", "num"]},
    "mizrahi":          {"name": "בנק מזרחי טפחות",     "category": "bank",        "fields": ["username", "password"]},
    "otsarHahayal":     {"name": "בנק אוצר החייל",      "category": "bank",        "fields": ["username", "password"]},
    "beinleumi":        {"name": "הבנק הבינלאומי",      "category": "bank",        "fields": ["username", "password"]},
    "massad":           {"name": "בנק מסד",             "category": "bank",        "fields": ["username", "password"]},
    "yahav":            {"name": "בנק יהב",             "category": "bank",        "fields": ["username", "password", "nationalID"]},
    "beyahadBishvilha": {"name": "בי-יחד בשבילך",       "category": "bank",        "fields": ["id", "password"]},
    "visaCal":          {"name": "ויזה כאל",            "category": "credit_card", "fields": ["username", "password"]},
    "max":              {"name": "מקס (לאומי קארד)",    "category": "credit_card", "fields": ["username", "password"]},
    "isracard":         {"name": "ישראכרט",             "category": "credit_card", "fields": ["id", "password", "card6Digits"]},
    "amex":             {"name": "אמריקן אקספרס",       "category": "credit_card", "fields": ["username", "password", "card6Digits"]},
}

MANUAL_INSTITUTIONS = {
    "phoenix":   {"name": "הפניקס",           "category": "insurance_pension"},
    "clal":      {"name": "כלל ביטוח",        "category": "insurance_pension"},
    "harel":     {"name": "הראל",             "category": "insurance_pension"},
    "menora":    {"name": "מנורה מבטחים",     "category": "insurance_pension"},
    "migdal":    {"name": "מגדל",             "category": "insurance_pension"},
    "meitav":    {"name": "מיטב",             "category": "investment_house"},
    "altshuler": {"name": "אלטשולר שחם",      "category": "investment_house"},
    "ibi":       {"name": "IBI",              "category": "investment_house"},
    "other":     {"name": "גוף אחר",          "category": "other"},
}

CATEGORY_LABELS = {
    "bank": "בנק",
    "credit_card": "כרטיס אשראי",
    "investment_house": "בית השקעות",
    "insurance_pension": "ביטוח ופנסיה",
    "other": "אחר",
}
