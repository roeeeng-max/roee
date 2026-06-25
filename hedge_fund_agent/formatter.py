"""
Format the daily WhatsApp message in Hebrew.
WhatsApp supports *bold*, _italic_, ~strikethrough~ and ```code```.
Max message size is ~1600 chars; long messages are split into chunks.
"""

from datetime import datetime
from typing import Optional

from analyzer import PositionChange

MAX_MSG_LEN = 1550  # leave headroom for Twilio overhead


def _usd(thousands: int) -> str:
    if thousands >= 1_000_000:
        return f"${thousands / 1_000_000:.1f}B"
    if thousands >= 1_000:
        return f"${thousands / 1_000:.1f}M"
    return f"${thousands}K"


def _top(items: list, key, n: int = 5) -> list:
    return sorted(items, key=key, reverse=True)[:n]


def _fund_block(update: dict) -> str:
    """Build the text block for one hedge fund update."""
    changes: list[PositionChange] = update["changes"]
    if not changes:
        return ""

    lines = [
        f"🏦 *{update['name']}*",
        f"📅 תקופה: {update['period']}  |  הוגש: {update['filed_date']}",
    ]

    new       = [c for c in changes if c.change_type == "new"]
    closed    = [c for c in changes if c.change_type == "closed"]
    increased = [c for c in changes if c.change_type == "increased"]
    decreased = [c for c in changes if c.change_type == "decreased"]

    if new:
        lines.append(f"\n🆕 פוזיציות חדשות ({len(new)}):")
        for c in _top(new, lambda x: x.current_value):
            lines.append(f"  • {c.issuer[:28]}  {_usd(c.current_value)}")

    if increased:
        lines.append(f"\n📈 הגדלות משמעותיות ({len(increased)}):")
        for c in _top(increased, lambda x: abs(x.change_pct or 0)):
            lines.append(
                f"  • {c.issuer[:22]}  +{c.change_pct:.0f}% → {_usd(c.current_value)}"
            )

    if decreased:
        lines.append(f"\n📉 הקטנות משמעותיות ({len(decreased)}):")
        for c in _top(decreased, lambda x: abs(x.change_pct or 0)):
            lines.append(
                f"  • {c.issuer[:22]}  {c.change_pct:.0f}% → {_usd(c.current_value)}"
            )

    if closed:
        lines.append(f"\n🔴 פוזיציות שנסגרו ({len(closed)}):")
        for c in _top(closed, lambda x: x.prev_value or 0):
            lines.append(f"  • {c.issuer[:28]}  (היה: {_usd(c.prev_value or 0)})")

    return "\n".join(lines)


def _ma_block(events: list[dict]) -> str:
    if not events:
        return ""
    form_labels = {
        "SC TO-T":  "הצעת רכישה (Tender Offer)",
        "SC TO-C":  "תגובה להצעת רכישה",
        "SC TO-I":  "הצעת רכישה עצמית",
        "SC-TO-T":  "הצעת רכישה (Tender Offer)",
        "SC 13D":   "רכישת >5% (13D)",
        "SC 13D/A": "עדכון רכישה (13D/A)",
    }
    lines = ["━━━━━━━━━━━━━━━", "🏢 *עסקאות רכישה / M&A*", ""]
    for ev in events:
        label = form_labels.get(ev["form"], ev["form"])
        lines.append(f"🏢 *{ev['company']}*  —  {label}")
        lines.append(f"   📅 {ev['filed_date']}")
        if ev.get("filing_url"):
            lines.append(f"   🔗 {ev['filing_url']}")
        lines.append("")
    return "\n".join(lines)


def build_messages(fund_updates: list[dict], ma_events: list[dict]) -> list[str]:
    """
    Returns a list of WhatsApp message strings.
    Splits into multiple messages if content exceeds MAX_MSG_LEN.
    Returns [] if there is nothing to report.
    """
    if not fund_updates and not ma_events:
        return []

    today = datetime.now().strftime("%d/%m/%Y")
    header = f"📊 *עדכון קרנות גידור — {today}*\n━━━━━━━━━━━━━━━\n"
    footer = "\n━━━━━━━━━━━━━━━\n_נשלח אוטומטית ע\"י סוכן ניטור שוק ההון_"

    sections: list[str] = []

    for upd in fund_updates:
        block = _fund_block(upd)
        if block:
            sections.append(block)

    ma = _ma_block(ma_events)
    if ma:
        sections.append(ma)

    if not sections:
        return []

    # Pack sections into messages ≤ MAX_MSG_LEN
    messages: list[str] = []
    current = header
    for section in sections:
        candidate = current + "\n\n" + section if current != header else header + section
        if len(candidate) + len(footer) <= MAX_MSG_LEN:
            current = candidate
        else:
            messages.append(current + footer)
            current = header + section

    messages.append(current + footer)
    return messages


def no_news_message() -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    return f"📊 *עדכון שוק ההון — {today}*\n\n✅ אין חדשות משמעותיות היום."
