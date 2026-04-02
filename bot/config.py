import os
from copy import deepcopy


def _merge_dicts(base, overrides):
    merged = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)
        else:
            merged[key] = value
    return merged


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

BOT_RULES = {
    "fast_drop_minutes": 30,
    "fast_drop_threshold": -0.02,
    "wti_high": 100.0,
    "wti_low": 90.0,
    "signal_cooldown_hours": 24,
    "stale_after_seconds": 900,
    "macro_windows": {
        "spy_minutes": 15,
        "vix_minutes": 15,
        "dxy_minutes": 30,
        "gold_minutes": 30,
    },
    "macro_thresholds": {
        "spy_drop": -0.02,
        "vix_jump": 0.10,
        "dxy_strength": 0.01,
        "gold_weakness": -0.01,
    },
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

try:
    from . import config_local as _config_local  # type: ignore
except ImportError:
    try:
        import config_local as _config_local  # type: ignore
    except ImportError:
        _config_local = None

if _config_local is not None:
    LOCAL_SYMBOLS = getattr(_config_local, "SYMBOLS", None)
    LOCAL_SYMBOL_METADATA = getattr(_config_local, "SYMBOL_METADATA", None)
    LOCAL_CHECK_INTERVAL = getattr(_config_local, "CHECK_INTERVAL", None)
    LOCAL_TELEGRAM_TOKEN = getattr(_config_local, "TELEGRAM_TOKEN", None)
    LOCAL_CHAT_ID = getattr(_config_local, "CHAT_ID", None)
    LOCAL_DB_CONFIG = getattr(_config_local, "DB_CONFIG", None)
    LOCAL_BOT_RULES = getattr(_config_local, "BOT_RULES", None)
    LOCAL_BUY_SIGNAL_RULES = getattr(_config_local, "BUY_SIGNAL_RULES", None)
else:
    LOCAL_SYMBOLS = None
    LOCAL_SYMBOL_METADATA = None
    LOCAL_CHECK_INTERVAL = None
    LOCAL_TELEGRAM_TOKEN = None
    LOCAL_CHAT_ID = None
    LOCAL_DB_CONFIG = None
    LOCAL_BOT_RULES = None
    LOCAL_BUY_SIGNAL_RULES = None

if LOCAL_SYMBOLS is not None:
    SYMBOLS = list(LOCAL_SYMBOLS)

if LOCAL_SYMBOL_METADATA is not None:
    SYMBOL_METADATA = _merge_dicts(SYMBOL_METADATA, LOCAL_SYMBOL_METADATA)

if LOCAL_CHECK_INTERVAL is not None:
    CHECK_INTERVAL = int(LOCAL_CHECK_INTERVAL)

if LOCAL_TELEGRAM_TOKEN is not None:
    TELEGRAM_TOKEN = LOCAL_TELEGRAM_TOKEN

if LOCAL_CHAT_ID is not None:
    CHAT_ID = LOCAL_CHAT_ID

if LOCAL_DB_CONFIG is not None:
    DB_CONFIG = _merge_dicts(DB_CONFIG, LOCAL_DB_CONFIG)

if LOCAL_BOT_RULES is not None:
    BOT_RULES = _merge_dicts(BOT_RULES, LOCAL_BOT_RULES)

if LOCAL_BUY_SIGNAL_RULES is not None:
    BUY_SIGNAL_RULES = _merge_dicts(BUY_SIGNAL_RULES, LOCAL_BUY_SIGNAL_RULES)
