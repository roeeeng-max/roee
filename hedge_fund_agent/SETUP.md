# הגדרת סוכן ניטור קרנות גידור

## מה הסוכן עושה?

כל יום בשעה 08:00 הסוכן:
1. **מוריד דיווחי 13F** מ-SEC EDGAR עבור 10 קרנות הגידור הגדולות בעולם
2. **מזהה שינויים משמעותיים** — פוזיציות חדשות, הגדלות/הקטנות >20%, פוזיציות שנסגרו
3. **עוקב אחרי עסקאות M&A** — SC-TO (הצעות רכישה) ורכישות >5% (13D) של חברות טק גדולות כמו Nvidia, Apple, Microsoft
4. **שולח סיכום לוואטסאפ** עם כל הממצאים

---

## שלב 1 — התקנת Python ו-dependencies

```bash
cd hedge_fund_agent
pip install -r requirements.txt
```

---

## שלב 2 — הגדרת Twilio (שליחת וואטסאפ)

### פתיחת חשבון חינמי
1. לך ל-[twilio.com/try-twilio](https://www.twilio.com/try-twilio) ופתח חשבון חינמי
2. אמת את מספר הטלפון שלך
3. בחר **"WhatsApp"** כערוץ

### הגדרת ה-Sandbox
1. בדאשבורד: **Messaging → Try it out → Send a WhatsApp message**
2. תראה הוראות לשלוח `join [קוד]` מהוואטסאפ שלך למספר `+1 415 523 8886`
3. שלח את ההודעה — זה מחבר את הוואטסאפ שלך ל-Sandbox

### קבלת ה-credentials
1. בדאשבורד לך ל-**Account → API keys & tokens**
2. העתק את:
   - **Account SID** (מתחיל ב-`AC...`)
   - **Auth Token**

---

## שלב 3 — יצירת קובץ .env

```bash
cp .env.example .env
```

ערוך את `.env`:
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+972501234567    # ← המספר שלך עם קידומת ישראל
DAILY_RUN_TIME=08:00
```

---

## שלב 4 — בדיקה ראשונה (dry run)

```bash
python main.py --dry
```

זה יבצע את כל הלוגיקה ויהדפיס את ההודעה למסך **בלי** לשלוח וואטסאפ.

---

## שלב 5 — הרצה ראשונה אמיתית

```bash
python main.py --once
```

שולח אם יש חדשות. אם הכל עובד — תקבל וואטסאפ.

---

## שלב 6 — הרצה יומית אוטומטית

### אפשרות א׳ — תהליך רץ ברקע (פשוט)
```bash
python main.py
```
(שמור את החלון פתוח, או הרץ עם `nohup python main.py &` על Linux)

### אפשרות ב׳ — cron (Linux/Mac — מומלץ לשרת)
```bash
crontab -e
```
הוסף שורה:
```
0 5 * * * cd /path/to/roee/hedge_fund_agent && python main.py --once >> /var/log/hedge_fund.log 2>&1
```
(5:00 UTC = 8:00 שעון ישראל)

### אפשרות ג׳ — Windows Task Scheduler
1. פתח Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 08:00
4. Action: `python C:\path\to\roee\hedge_fund_agent\main.py --once`

---

## אימות CIK של קרנות גידור

אם קרן לא נמצאת, אפשר לחפש את ה-CIK שלה:
```bash
python find_cik.py "Bridgewater Associates"
python find_cik.py "Citadel Advisors"
```

ועדכן את `config.py` בהתאם.

---

## הגדרות ב-config.py

| הגדרה | ברירת מחדל | משמעות |
|-------|-----------|--------|
| `MIN_POSITION_VALUE_K` | 5000 | פוזיציות קטנות מ-$5M מוסתרות |
| `MIN_CHANGE_PCT` | 20% | רק שינויים >20% מדווחים |
| `SEND_IF_NO_NEWS` | false | לא שולח אם אין חדשות |

---

## מקורות הנתונים

- **13F filings** — SEC EDGAR (חינם, ציבורי). מוגשים אחת לרבעון בתוך 45 יום מסוף הרבעון.
- **SC-TO / 13D** — SEC EDGAR. מוגשים כשחברה רוכשת >5% ממניות חברה ציבורית, או מגישה הצעת רכישה.
- אין API key נוסף הנדרש — הכל חינמי מה-SEC.

---

## דוגמה להודעת וואטסאפ

```
📊 עדכון קרנות גידור — 25/06/2026
━━━━━━━━━━━━━━━

🏦 Citadel Advisors
📅 תקופה: 2026-03-31 | הוגש: 2026-05-12

🆕 פוזיציות חדשות (3):
  • NVIDIA CORP              $234.5M
  • TAIWAN SEMICONDUCTOR     $89.3M
  • ARM HOLDINGS             $45.1M

📈 הגדלות משמעותיות (2):
  • AMAZON.COM INC    +67% → $1.2B
  • META PLATFORMS    +34% → $456M

━━━━━━━━━━━━━━━
🏢 עסקאות רכישה / M&A

🏢 Nvidia  —  הצעת רכישה (Tender Offer)
   📅 2026-06-24
   🔗 https://www.sec.gov/Archives/edgar/data/...

━━━━━━━━━━━━━━━
_נשלח אוטומטית ע"י סוכן ניטור שוק ההון_
```
