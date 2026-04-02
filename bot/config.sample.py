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
