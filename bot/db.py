import mysql.connector
from datetime import datetime

try:
    from .config import DB_CONFIG
except ImportError:
    from config import DB_CONFIG

def get_conn():
    return mysql.connector.connect(**DB_CONFIG, autocommit=True)

def save_price(conn, symbol, price):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO prices (symbol, price, timestamp) VALUES (%s, %s, %s)",
        (symbol, float(price), datetime.utcnow())
    )

def save_signal(conn, symbol, type_, value, message):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO signals (symbol, type, value, message, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (symbol, type_, float(value) if value else None, message, datetime.utcnow())
    )

def signal_exists(conn, symbol, type_):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1 FROM signals
        WHERE symbol=%s AND type=%s
        AND created_at > NOW() - INTERVAL 1 DAY
        LIMIT 1
        """,
        (symbol, type_)
    )
    return cursor.fetchone() is not None

def get_velocity(conn, symbol, minutes=30):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT MIN(price), MAX(price)
        FROM prices
        WHERE symbol=%s
        AND timestamp > NOW() - INTERVAL %s MINUTE
        """,
        (symbol, minutes)
    )
    low, high = cursor.fetchone()
    if low and high and low != 0:
        return float((high - low) / low)
    return 0.0

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
        (symbol, limit)
    )
    return cursor.fetchall()
