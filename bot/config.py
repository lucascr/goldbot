import os
from copy import deepcopy


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

CHECK_INTERVAL = int(os.getenv("GOLDBOT_CHECK_INTERVAL", "300"))

TELEGRAM_TOKEN = os.getenv("GOLDBOT_TELEGRAM_TOKEN", "")
CHAT_ID = os.getenv("GOLDBOT_CHAT_ID", "")

DB_CONFIG = {
    "host": os.getenv("GOLDBOT_DB_HOST", "localhost"),
    "user": os.getenv("GOLDBOT_DB_USER", "root"),
    "password": os.getenv("GOLDBOT_DB_PASSWORD", ""),
    "database": os.getenv("GOLDBOT_DB_NAME", "goldbot"),
}

try:
    from .config_local import (  # type: ignore
        CHAT_ID as LOCAL_CHAT_ID,
        CHECK_INTERVAL as LOCAL_CHECK_INTERVAL,
        DB_CONFIG as LOCAL_DB_CONFIG,
        SYMBOL_METADATA as LOCAL_SYMBOL_METADATA,
        SYMBOLS as LOCAL_SYMBOLS,
        TELEGRAM_TOKEN as LOCAL_TELEGRAM_TOKEN,
    )
except ImportError:
    try:
        from config_local import (  # type: ignore
            CHAT_ID as LOCAL_CHAT_ID,
            CHECK_INTERVAL as LOCAL_CHECK_INTERVAL,
            DB_CONFIG as LOCAL_DB_CONFIG,
            SYMBOL_METADATA as LOCAL_SYMBOL_METADATA,
            SYMBOLS as LOCAL_SYMBOLS,
            TELEGRAM_TOKEN as LOCAL_TELEGRAM_TOKEN,
        )
    except ImportError:
        LOCAL_SYMBOLS = None
        LOCAL_CHECK_INTERVAL = None
        LOCAL_TELEGRAM_TOKEN = None
        LOCAL_CHAT_ID = None
        LOCAL_DB_CONFIG = None
        LOCAL_SYMBOL_METADATA = None

if LOCAL_SYMBOLS is not None:
    SYMBOLS = list(LOCAL_SYMBOLS)

if LOCAL_CHECK_INTERVAL is not None:
    CHECK_INTERVAL = int(LOCAL_CHECK_INTERVAL)

if LOCAL_TELEGRAM_TOKEN is not None:
    TELEGRAM_TOKEN = LOCAL_TELEGRAM_TOKEN

if LOCAL_CHAT_ID is not None:
    CHAT_ID = LOCAL_CHAT_ID

if LOCAL_DB_CONFIG is not None:
    merged_db_config = deepcopy(DB_CONFIG)
    merged_db_config.update(LOCAL_DB_CONFIG)
    DB_CONFIG = merged_db_config

if LOCAL_SYMBOL_METADATA is not None:
    merged_symbol_metadata = deepcopy(SYMBOL_METADATA)
    merged_symbol_metadata.update(LOCAL_SYMBOL_METADATA)
    SYMBOL_METADATA = merged_symbol_metadata
