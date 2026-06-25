import logging

from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM, WHATSAPP_TO

log = logging.getLogger(__name__)


def send_whatsapp(messages: list[str]) -> bool:
    """
    Send one or more WhatsApp messages via Twilio.
    Prints the messages to stdout if credentials are not configured (dry-run mode).
    Returns True if all messages were sent successfully.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WHATSAPP_TO]):
        log.warning("Twilio credentials not set — printing to stdout instead.")
        for i, msg in enumerate(messages, 1):
            print(f"\n{'─'*60}\n[WhatsApp message {i}/{len(messages)}]\n{msg}\n")
        return True

    try:
        from twilio.rest import Client  # noqa: PLC0415
    except ImportError:
        log.error("twilio package not installed. Run: pip install twilio")
        return False

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    success = True
    for msg in messages:
        try:
            result = client.messages.create(body=msg, from_=TWILIO_FROM, to=WHATSAPP_TO)
            log.info(f"WhatsApp sent: {result.sid}")
        except Exception as exc:
            log.error(f"WhatsApp send failed: {exc}")
            success = False

    return success
