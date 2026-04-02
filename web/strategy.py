import sys
from pathlib import Path

try:
    from bot.db import save_signal, signal_exists, get_velocity
except ImportError:
    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    from bot.db import save_signal, signal_exists, get_velocity

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
