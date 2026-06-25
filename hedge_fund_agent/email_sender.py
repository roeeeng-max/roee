"""
Send the daily report as an HTML email via Gmail SMTP.
Uses an App Password (not your regular Gmail password).
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from config import GMAIL_USER, GMAIL_APP_PASSWORD, EMAIL_TO

log = logging.getLogger(__name__)


def _to_html(messages: list[str]) -> str:
    """Convert plain-text WhatsApp-style messages to a clean HTML email body."""
    today = datetime.now().strftime("%d/%m/%Y")
    body = ""
    for msg in messages:
        for line in msg.split("\n"):
            line_h = (
                line
                .replace("*", "<b>", 1).replace("*", "</b>", 1)  # *bold*
                .replace("━━━━━━━━━━━━━━━", "<hr>")
                .replace("📊", "📊").replace("🏦", "🏦")
            )
            if line_h.strip() == "<hr>":
                body += "<hr style='border:1px solid #ddd;margin:12px 0'>"
            elif line_h.strip() == "":
                body += "<br>"
            else:
                body += f"<p style='margin:2px 0;font-family:monospace'>{line_h}</p>"

    return f"""
    <html><body style="background:#f8f9fa;padding:20px">
      <div style="max-width:600px;margin:auto;background:#fff;
                  border-radius:8px;padding:24px;font-size:14px;
                  border:1px solid #e0e0e0">
        <h2 style="color:#1a1a2e;border-bottom:2px solid #4CAF50;
                   padding-bottom:8px">📊 עדכון קרנות גידור — {today}</h2>
        {body}
        <p style="color:#999;font-size:11px;margin-top:20px;border-top:1px solid #eee;
                  padding-top:10px">נשלח אוטומטית ע"י סוכן ניטור שוק ההון</p>
      </div>
    </body></html>
    """


def send_email(messages: list[str]) -> bool:
    """
    Send messages as an HTML email via Gmail.
    Falls back to stdout print if credentials are not set.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        log.warning("Gmail credentials not configured — printing to stdout.")
        for i, msg in enumerate(messages, 1):
            print(f"\n{'─'*60}\n[Email message {i}]\n{msg}\n")
        return True

    today = datetime.now().strftime("%d/%m/%Y")
    subject = f"📊 עדכון קרנות גידור — {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = GMAIL_USER
    msg["To"]      = EMAIL_TO

    plain = "\n\n".join(messages)
    html  = _to_html(messages)

    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
        log.info(f"Email sent to {EMAIL_TO}")
        return True
    except Exception as exc:
        log.error(f"Email send failed: {exc}")
        return False
