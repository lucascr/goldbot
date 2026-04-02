import mysql.connector
from datetime import datetime

try:
    from .config import BOT_RULES, DB_CONFIG
except ImportError:
    from config import BOT_RULES, DB_CONFIG


def get_conn():
    return mysql.connector.connect(**DB_CONFIG, autocommit=True)


def save_price(conn, symbol, price):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prices (symbol, price, timestamp) VALUES (%s, %s, %s)",
        (symbol, float(price), datetime.utcnow()),
    )


def save_signal(conn, symbol, type_, value, message):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO signals (symbol, type, value, message, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (symbol, type_, float(value) if value is not None else None, message, datetime.utcnow()),
    )


def signal_exists(conn, symbol, type_):
    cooldown_hours = int(BOT_RULES.get("signal_cooldown_hours", 24))
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT 1 FROM signals
        WHERE symbol=%s AND type=%s
        AND created_at > NOW() - INTERVAL {cooldown_hours} HOUR
        LIMIT 1
        """,
        (symbol, type_),
    )
    return cursor.fetchone() is not None


def _get_window_edge_prices(conn, symbol, minutes):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT price, timestamp
        FROM prices
        WHERE symbol=%s
        AND timestamp > NOW() - INTERVAL %s MINUTE
        ORDER BY timestamp ASC
        """,
        (symbol, minutes),
    )
    rows = cursor.fetchall()
    if len(rows) < 2:
        return None, None
    return rows[0], rows[-1]


def get_directional_change(conn, symbol, minutes=30):
    first_row, last_row = _get_window_edge_prices(conn, symbol, minutes)
    if not first_row or not last_row:
        return 0.0

    first_price = float(first_row[0])
    last_price = float(last_row[0])
    if first_price == 0:
        return 0.0
    return (last_price - first_price) / first_price


def get_velocity(conn, symbol, minutes=30):
    return get_directional_change(conn, symbol, minutes)


def get_prices(conn, symbol, limit=200):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT price, timestamp
        FROM prices
        WHERE symbol=%s
        ORDER BY timestamp DESC
        LIMIT %s
        """,
        (symbol, limit),
    )
    return cursor.fetchall()
