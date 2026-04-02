import logging
import time

import requests

try:
    from .config import CHECK_INTERVAL, SYMBOLS
    from .db import get_conn, save_price
    from .logging_utils import configure_logging
    from .status import update_runtime_status, utc_now_iso
    from .strategy import check_drop, check_wti
    from .telegram import send_telegram_message
except ImportError:
    from config import CHECK_INTERVAL, SYMBOLS
    from db import get_conn, save_price
    from logging_utils import configure_logging
    from status import update_runtime_status, utc_now_iso
    from strategy import check_drop, check_wti
    from telegram import send_telegram_message


logger = logging.getLogger("goldbot.bot")


def get_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["chart"]["result"][0]["meta"]["regularMarketPrice"]


def send(message):
    send_telegram_message(message)
    update_runtime_status(last_telegram_at=utc_now_iso(), last_telegram_message=message, last_error=None)
    logger.info("Telegram message sent")


def run():
    configure_logging()
    logger.info("Starting Goldbot for %d symbols", len(SYMBOLS))
    update_runtime_status(status="starting", last_error=None)

    conn = get_conn()
    update_runtime_status(status="connected", last_error=None)

    while True:
        try:
            update_runtime_status(status="polling", last_loop_at=utc_now_iso(), last_error=None)

            for symbol in SYMBOLS:
                update_runtime_status(current_symbol=symbol)
                try:
                    price = get_price(symbol)
                    logger.info("Fetched %s at %.4f", symbol, price)
                except Exception as exc:
                    logger.warning("Fetch error for %s: %s", symbol, exc)
                    update_runtime_status(last_error=f"Fetch error for {symbol}: {exc}", current_symbol=symbol)
                    continue

                save_price(conn, symbol, price)
                update_runtime_status(
                    last_symbol=symbol,
                    last_price=price,
                    last_price_save_at=utc_now_iso(),
                    last_error=None,
                )

                try:
                    if symbol == "CL=F":
                        check_wti(conn, price, send)
                    else:
                        check_drop(conn, symbol, price, send)
                except Exception as exc:
                    logger.exception("Strategy error for %s", symbol)
                    update_runtime_status(last_error=f"Strategy error for {symbol}: {exc}")

        except Exception as exc:
            logger.exception("Loop error")
            update_runtime_status(status="error", last_error=f"Loop error: {exc}")
        else:
            update_runtime_status(status="sleeping", sleep_seconds=CHECK_INTERVAL)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
