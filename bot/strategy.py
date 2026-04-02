import logging

try:
    from .config import BOT_RULES
    from .db import get_directional_change, save_signal, signal_exists
except ImportError:
    from config import BOT_RULES
    from db import get_directional_change, save_signal, signal_exists


logger = logging.getLogger("goldbot.strategy")


def check_drop(conn, symbol, price, send):
    minutes = int(BOT_RULES["fast_drop_minutes"])
    threshold = float(BOT_RULES["fast_drop_threshold"])
    change = get_directional_change(conn, symbol, minutes)

    if change <= threshold and not signal_exists(conn, symbol, "FAST_DROP"):
        message = f"{symbol} FAST DROP | {minutes}m: {change * 100:.2f}% | price: {price}"
        logger.info("Triggering FAST_DROP for %s at %.4f", symbol, price)
        send(message)
        save_signal(conn, symbol, "FAST_DROP", change, message)


def check_wti(conn, price, send):
    high = float(BOT_RULES["wti_high"])
    low = float(BOT_RULES["wti_low"])

    if price >= high and not signal_exists(conn, "CL=F", "WTI_HIGH"):
        message = f"WTI HIGH -> {price}"
        logger.info("Triggering WTI_HIGH at %.4f", price)
        send(message)
        save_signal(conn, "CL=F", "WTI_HIGH", price, message)
    elif price <= low and not signal_exists(conn, "CL=F", "WTI_LOW"):
        message = f"WTI LOW -> {price}"
        logger.info("Triggering WTI_LOW at %.4f", price)
        send(message)
        save_signal(conn, "CL=F", "WTI_LOW", price, message)


def check_macro(conn, send):
    macro_windows = BOT_RULES["macro_windows"]
    macro_thresholds = BOT_RULES["macro_thresholds"]

    spy = get_directional_change(conn, "SPY", macro_windows["spy_minutes"])
    vix = get_directional_change(conn, "^VIX", macro_windows["vix_minutes"])
    dxy = get_directional_change(conn, "DX-Y.NYB", macro_windows["dxy_minutes"])
    gold = get_directional_change(conn, "GLDM", macro_windows["gold_minutes"])

    if spy <= macro_thresholds["spy_drop"] and vix >= macro_thresholds["vix_jump"]:
        send("CRASH SETUP")

    if dxy >= macro_thresholds["dxy_strength"] and gold <= macro_thresholds["gold_weakness"]:
        send("USD STRENGTH")
