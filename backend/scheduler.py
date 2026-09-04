# סנכרון אוטומטי ברקע - פעם ביום מרענן את כל החיבורים האוטומטיים (בנקים/
# כרטיסי אשראי). אם הכספת נעולה (למשל אחרי הפעלה מחדש של השרת) - הג'וב
# פשוט מדלג, והמשתמש צריך לפתוח את הכספת שוב מהממשק כדי שהסנכרון האוטומטי
# ימשיך.
from apscheduler.schedulers.background import BackgroundScheduler

import vault
from database import SessionLocal
from models import BankConnection
from sync_service import sync_connection

scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")


def _daily_sync_job():
    if not vault.is_unlocked():
        return
    db = SessionLocal()
    try:
        connections = db.query(BankConnection).filter(BankConnection.kind == "scraped").all()
        for conn in connections:
            sync_connection(db, conn)
    finally:
        db.close()


def start_scheduler():
    if scheduler.running:
        return
    scheduler.add_job(_daily_sync_job, "cron", hour=6, minute=30, id="daily_sync", replace_existing=True)
    scheduler.start()
