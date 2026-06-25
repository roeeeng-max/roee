# הגדרת סוכן ניטור קרנות גידור

## מה הסוכן עושה?

כל יום בשעה 08:00 הסוכן:
1. **מוריד דיווחי 13F** מ-SEC EDGAR עבור 10 קרנות הגידור הגדולות בעולם
2. **מזהה שינויים משמעותיים** — פוזיציות חדשות, הגדלות/הקטנות >20%, פוזיציות שנסגרו
3. **עוקב אחרי עסקאות M&A** — SC-TO (הצעות רכישה) ורכישות >5% (13D) של חברות טק גדולות
4. **שולח סיכום לוואטסאפ** דרך CallMeBot (חינמי, ללא Twilio)

---

## שלב 1 — התקנת Python ו-dependencies

```bash
cd hedge_fund_agent
pip install -r requirements.txt
```

---

## שלב 2 — הגדרת CallMeBot (שליחה לוואטסאפ, חינמי)

### הרשמה חד-פעמית (2 דקות)

1. **שמור את המספר** `+34 644 47 62 26` באנשי הקשר שלך בוואטסאפ (שם: "CallMeBot")
2. **שלח** מהוואטסאפ שלך לאותו מספר את ההודעה הזו **בדיוק**:
   ```
   I allow callmebot to send me messages
   ```
3. תוך כמה שניות תקבל הודעה חזרה עם **API Key** (מספר בן 7 ספרות)

---

## שלב 3 — יצירת קובץ .env

```bash
cp .env.example .env
```

ערוך את `.env`:
```
CALLMEBOT_PHONE=+972501234567    # ← המספר שלך (עם +972)
CALLMEBOT_APIKEY=1234567         # ← ה-API key שקיבלת
DAILY_RUN_TIME=08:00
```

---

## שלב 4 — בדיקה ראשונה (dry run)

```bash
python main.py --dry
```

מבצע את כל הלוגיקה ומדפיס את ההודעה למסך **בלי** לשלוח וואטסאפ.

---

## שלב 5 — הרצה ראשונה אמיתית

```bash
python main.py --once
```

שולח לוואטסאפ אם יש חדשות.

---

## שלב 6 — הרצה יומית אוטומטית

### אפשרות א׳ — תהליך רץ ברקע (הכי פשוט)
```bash
python main.py
```
על Linux/Mac אפשר להריץ ברקע:
```bash
nohup python main.py > hedge_fund.log 2>&1 &
```

### אפשרות ב׳ — cron (Linux/Mac — מומלץ לשרת)
```bash
crontab -e
```
הוסף שורה (5 UTC = 8 שעון ישראל):
```
0 5 * * * cd /full/path/to/roee/hedge_fund_agent && python main.py --once >> /var/log/hedge_fund.log 2>&1
```

### אפשרות ג׳ — Windows Task Scheduler
1. פתח **Task Scheduler**
2. **Create Basic Task**
3. Trigger: **Daily** at 08:00
4. Action: `python C:\full\path\to\roee\hedge_fund_agent\main.py --once`

---

## אימות CIK של קרנות גידור

```bash
python find_cik.py "Bridgewater Associates"
python find_cik.py "Citadel Advisors"
```
ועדכן את `config.py` בהתאם.

---

## הגדרות ב-.env

| משתנה | ברירת מחדל | משמעות |
|-------|-----------|--------|
| `CALLMEBOT_PHONE` | — | המספר שלך עם +972 |
| `CALLMEBOT_APIKEY` | — | מ-CallMeBot |
| `DAILY_RUN_TIME` | 08:00 | שעת שליחה |
| `SEND_IF_NO_NEWS` | false | לשלוח גם אם אין חדשות |
| `MIN_POSITION_VALUE` | 5000 | פוזיציות מתחת ל-$5M מוסתרות |
| `MIN_CHANGE_PCT` | 20.0 | רק שינויים >20% מדווחים |

---

## דוגמה להודעת וואטסאפ

```
📊 עדכון קרנות גידור — 25/06/2026
━━━━━━━━━━━━━━━

🏦 Citadel Advisors
📅 תקופה: 2026-03-31  |  הוגש: 2026-05-12

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

---

## מקורות הנתונים

- **13F filings** — SEC EDGAR (חינמי, ציבורי). מוגשים רבעונית בתוך 45 יום מסוף הרבעון.
- **SC-TO / 13D** — SEC EDGAR. מוגשים כשחברה רוכשת >5% ממניות חברה ציבורית, או מגישה הצעת רכישה.
- אין API key נוסף — הכל חינמי מה-SEC.
