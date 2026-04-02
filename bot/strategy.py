try:
    from .db import save_signal, signal_exists, get_velocity
except ImportError:
    from db import save_signal, signal_exists, get_velocity

def check_drop(conn, symbol, price, send):
    vel = get_velocity(conn, symbol, 30)

    if vel < -0.02 and not signal_exists(conn, symbol, "FAST_DROP"):
        msg = f"⚡ {symbol} FAST DROP\n30min: {vel*100:.2f}%"
        send(msg)
        save_signal(conn, symbol, "FAST_DROP", vel, msg)


def check_wti(conn, price, send):
    HIGH = 100
    LOW = 90

    if price >= HIGH and not signal_exists(conn, "CL=F", "WTI_HIGH"):
        msg = f"🛢️ WTI HIGH → {price}"
        send(msg)
        save_signal(conn, "CL=F", "WTI_HIGH", price, msg)

    elif price <= LOW and not signal_exists(conn, "CL=F", "WTI_LOW"):
        msg = f"🛢️ WTI LOW → {price}"
        send(msg)
        save_signal(conn, "CL=F", "WTI_LOW", price, msg)


def check_macro(conn, send):
    spy = get_velocity(conn, "SPY", 15)
    vix = get_velocity(conn, "^VIX", 15)
    dxy = get_velocity(conn, "DX-Y.NYB", 30)
    gold = get_velocity(conn, "GLDM", 30)

    if spy < -0.02 and vix > 0.10:
        send("🚨 CRASH SETUP")

    if dxy > 0.01 and gold < -0.01:
        send("💵 USD STRENGTH")
