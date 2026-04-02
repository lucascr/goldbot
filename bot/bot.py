import requests
import time

try:
    from .config import SYMBOLS, CHECK_INTERVAL
    from .db import get_conn, save_price
    from .strategy import check_drop, check_wti
    from .telegram import send_telegram_message
except ImportError:
    from config import SYMBOLS, CHECK_INTERVAL
    from db import get_conn, save_price
    from strategy import check_drop, check_wti
    from telegram import send_telegram_message

def get_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}

    res = requests.get(url, headers=headers, timeout=10)
    data = res.json()

    return data["chart"]["result"][0]["meta"]["regularMarketPrice"]

def send(msg):
    send_telegram_message(msg)

def run():
    conn = get_conn()

    while True:
        try:
            for symbol in SYMBOLS:
                try:
                    price = get_price(symbol)
                except Exception as e:
                    print("Fetch error:", symbol, e)
                    continue

                print(symbol, price)

                save_price(conn, symbol, price)

                if symbol == "CL=F":
                    check_wti(conn, price, send)
                else:
                    check_drop(conn, symbol, price, send)

        except Exception as e:
            print("Loop error:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    run()
