import requests

try:
    from .config import CHAT_ID, TELEGRAM_TOKEN
except ImportError:
    from config import CHAT_ID, TELEGRAM_TOKEN


def send_telegram_message(message: str):
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message},
        timeout=10,
    )
    if not response.ok:
        try:
            detail = response.json()
        except ValueError:
            detail = {"description": response.text}
        description = detail.get("description", response.text)
        raise RuntimeError(f"Telegram send failed: {description}")
    return response.json()
