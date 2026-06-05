import os
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return False
    try:
        resp = requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            print("Message sent successfully to Telegram")
            return True
        else:
            print(f"Telegram API error: {resp.status_code} {resp.text}")
            return False
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False
