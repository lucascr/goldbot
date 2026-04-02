SYMBOLS = [
    "GLDM",
    "SI=F",
    "SPY",
    "CL=F",
    "^VIX",
    "^TNX",
    "DX-Y.NYB",
]

SYMBOL_METADATA = {
    "GLDM": {"name": "SPDR Gold MiniShares Trust", "label": "Gold ETF"},
    "SI=F": {"name": "Silver Futures", "label": "Silver"},
    "SPY": {"name": "SPDR S&P 500 ETF Trust", "label": "S&P 500 ETF"},
    "CL=F": {"name": "WTI Crude Oil Futures", "label": "Crude Oil"},
    "^VIX": {"name": "CBOE Volatility Index", "label": "Volatility"},
    "^TNX": {"name": "CBOE 10-Year Treasury Note Yield", "label": "10Y Yield"},
    "DX-Y.NYB": {"name": "US Dollar Index", "label": "Dollar Index"},
}

CHECK_INTERVAL = 300

TELEGRAM_TOKEN = "replace-with-your-telegram-bot-token"
CHAT_ID = "replace-with-your-chat-id"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "replace-with-your-db-password",
    "database": "goldbot",
}

BOT_RULES = {
    "fast_drop_minutes": 30,
    "fast_drop_threshold": -0.02,
    "wti_high": 100.0,
    "wti_low": 90.0,
    "signal_cooldown_hours": 24,
    "stale_after_seconds": 900,
}

BUY_SIGNAL_RULES = {
    "rsi_oversold": 35.0,
    "minimum_confidence": 2,
    "timeframes": [
        {"key": "15m", "minutes": 15, "drop_threshold": -0.008},
        {"key": "30m", "minutes": 30, "drop_threshold": -0.015},
        {"key": "1h", "minutes": 60, "drop_threshold": -0.022},
        {"key": "4h", "minutes": 240, "drop_threshold": -0.035},
    ],
}
