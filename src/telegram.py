import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

MAX_MSG_LEN = 4000


def send_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False

    parts = []
    while len(text) > MAX_MSG_LEN:
        split_at = text.rfind("\n", 0, MAX_MSG_LEN)
        if split_at == -1:
            split_at = MAX_MSG_LEN
        parts.append(text[:split_at])
        text = text[split_at:].strip()
    if text:
        parts.append(text)

    success = True
    for i, part in enumerate(parts):
        try:
            resp = requests.post(
                f"{API_URL}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": part,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                print(f"Part {i+1}/{len(parts)} sent successfully")
            else:
                print(f"Telegram API error (part {i+1}): {resp.status_code} {resp.text}")
                success = False
        except Exception as e:
            print(f"Telegram send failed (part {i+1}): {e}")
            success = False

    if success:
        print("All parts delivered to Telegram")
    return success
