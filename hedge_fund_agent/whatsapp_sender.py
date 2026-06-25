"""
Send WhatsApp messages via CallMeBot (free, no Twilio needed).

Setup (one-time):
1. Add +34 644 47 62 26 to your WhatsApp contacts.
2. Send: "I allow callmebot to send me messages"
3. You will receive an API key — put it in .env as CALLMEBOT_APIKEY.

API endpoint: https://api.callmebot.com/whatsapp.php?phone=...&text=...&apikey=...
"""

import logging
import time
import urllib.parse

import requests

from config import CALLMEBOT_PHONE, CALLMEBOT_APIKEY

log = logging.getLogger(__name__)

_URL = "https://api.callmebot.com/whatsapp.php"
# CallMeBot caps messages at ~800 chars reliably
_MAX_CHUNK = 750


def _chunks(text: str) -> list[str]:
    """Split a long message into CallMeBot-safe chunks on newline boundaries."""
    if len(text) <= _MAX_CHUNK:
        return [text]

    parts: list[str] = []
    current = ""
    for line in text.split("\n"):
        candidate = (current + "\n" + line).lstrip("\n")
        if len(candidate) <= _MAX_CHUNK:
            current = candidate
        else:
            if current:
                parts.append(current)
            current = line
    if current:
        parts.append(current)
    return parts or [text[: _MAX_CHUNK]]


def send_whatsapp(messages: list[str]) -> bool:
    """
    Send one or more messages to WhatsApp via CallMeBot.
    Each message is further split if it exceeds 750 chars.
    Prints to stdout when credentials are not configured (dry-run).
    Returns True if everything was sent successfully.
    """
    if not CALLMEBOT_PHONE or not CALLMEBOT_APIKEY:
        log.warning("CallMeBot credentials not set — printing to stdout instead.")
        for i, msg in enumerate(messages, 1):
            print(f"\n{'─'*60}\n[WhatsApp message {i}/{len(messages)}]\n{msg}\n")
        return True

    success = True
    chunks_all: list[str] = []
    for msg in messages:
        chunks_all.extend(_chunks(msg))

    for i, chunk in enumerate(chunks_all):
        params = {
            "phone":  CALLMEBOT_PHONE,
            "text":   chunk,
            "apikey": CALLMEBOT_APIKEY,
        }
        try:
            resp = requests.get(_URL, params=params, timeout=15)
            if resp.status_code == 200:
                log.info(f"WhatsApp chunk {i+1}/{len(chunks_all)} sent OK")
            else:
                log.error(f"CallMeBot returned {resp.status_code}: {resp.text[:120]}")
                success = False
        except Exception as exc:
            log.error(f"WhatsApp send failed: {exc}")
            success = False

        if i < len(chunks_all) - 1:
            time.sleep(2)  # CallMeBot rate-limit: be gentle

    return success
