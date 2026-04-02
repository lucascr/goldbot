import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

try:
    from bot.config import BOT_RULES, SYMBOLS, SYMBOL_METADATA
    from bot.db import get_conn, get_prices
    from bot.status import read_runtime_status
    from bot.telegram import send_telegram_message
except ImportError:
    repo_root = Path(__file__).resolve().parent.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    from bot.config import BOT_RULES, SYMBOLS, SYMBOL_METADATA
    from bot.db import get_conn, get_prices
    from bot.status import read_runtime_status
    from bot.telegram import send_telegram_message

try:
    from .buy_signals import check_buy_zone
    from .dashboard import render_dashboard
    from .indicators import build_indicator_history, compute_indicators
except ImportError:
    from buy_signals import check_buy_zone
    from dashboard import render_dashboard
    from indicators import build_indicator_history, compute_indicators


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
STALE_AFTER_SECONDS = int(BOT_RULES["stale_after_seconds"])
STREAM_INTERVAL_SECONDS = 8
DEFAULT_HISTORY_LIMIT = 120

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def _safe_close(conn):
    if conn is None:
        return
    try:
        conn.close()
    except Exception:
        pass


def _serialize_prices(rows):
    serialized = []
    for price, timestamp in rows:
        serialized.append(
            {
                "price": float(price),
                "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
            }
        )
    return serialized


def _is_stale(timestamp):
    if timestamp is None:
        return True
    dt = timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(str(timestamp))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt).total_seconds() > STALE_AFTER_SECONDS


def _database_http_error(exc):
    raise HTTPException(status_code=500, detail=f"Market data is unavailable: {exc}")


def _build_stale_flags(rows):
    latest_timestamp = rows[0][1] if rows else None
    return latest_timestamp, _is_stale(latest_timestamp)


def build_symbol_snapshot(conn, symbol: str, limit: int = DEFAULT_HISTORY_LIMIT):
    symbol_meta = SYMBOL_METADATA.get(symbol, {})
    rows = get_prices(conn, symbol, limit)
    latest_timestamp, is_stale = _build_stale_flags(rows)
    indicators = compute_indicators(rows) if len(rows) >= 20 else {}
    signals = check_buy_zone(conn, symbol, indicators, rows=rows) if indicators else None
    history = build_indicator_history(rows)
    latest_price = float(rows[0][0]) if rows else None

    return {
        "symbol": symbol,
        "name": symbol_meta.get("name", symbol),
        "label": symbol_meta.get("label", symbol),
        "price": latest_price,
        "updated_at": latest_timestamp.isoformat() if latest_timestamp else None,
        "is_stale": is_stale,
        "history": history,
        "prices": _serialize_prices(rows),
        "indicators": indicators or None,
        "signals": signals,
    }


def build_overview_item(conn, symbol: str):
    symbol_meta = SYMBOL_METADATA.get(symbol, {})
    snapshot = build_symbol_snapshot(conn, symbol, limit=80)
    timeframes = snapshot["signals"]["timeframes"] if snapshot["signals"] else []
    change_1h = next((item["change"] for item in timeframes if item["timeframe"] == "1h"), None)

    return {
        "symbol": symbol,
        "name": symbol_meta.get("name", symbol),
        "label": symbol_meta.get("label", symbol),
        "price": snapshot["price"],
        "rsi": snapshot["indicators"]["rsi"] if snapshot["indicators"] else None,
        "ma20": snapshot["indicators"]["ma20"] if snapshot["indicators"] else None,
        "signal_summary": snapshot["signals"]["summary"] if snapshot["signals"] else "WAIT",
        "active_timeframes": snapshot["signals"]["active_timeframes"] if snapshot["signals"] else [],
        "change_1h": change_1h,
        "updated_at": snapshot["updated_at"],
        "is_stale": snapshot["is_stale"],
    }


def build_market_frame(active_symbol: str | None = None):
    conn = get_conn()
    try:
        overview = [build_overview_item(conn, symbol) for symbol in SYMBOLS]
        focus_symbol = active_symbol or (SYMBOLS[0] if SYMBOLS else None)
        detail = build_symbol_snapshot(conn, focus_symbol) if focus_symbol else None
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overview": overview,
            "detail": detail,
            "bot_health": read_runtime_status(),
        }
    finally:
        _safe_close(conn)


@app.get("/", response_class=HTMLResponse)
def root():
    return render_dashboard(SYMBOLS, SYMBOL_METADATA)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/bot/health")
def bot_health():
    return read_runtime_status()


@app.get("/overview")
def overview():
    try:
        conn = get_conn()
        try:
            return [build_overview_item(conn, symbol) for symbol in SYMBOLS]
        finally:
            _safe_close(conn)
    except Exception as exc:
        _database_http_error(exc)


@app.get("/snapshot/{symbol}")
def snapshot(symbol: str):
    try:
        conn = get_conn()
        try:
            return build_symbol_snapshot(conn, symbol)
        finally:
            _safe_close(conn)
    except Exception as exc:
        _database_http_error(exc)


@app.get("/prices/{symbol}")
def prices(symbol: str):
    try:
        conn = get_conn()
        try:
            return {"data": get_prices(conn, symbol)}
        finally:
            _safe_close(conn)
    except Exception as exc:
        _database_http_error(exc)


@app.get("/indicators/{symbol}")
def indicators(symbol: str):
    try:
        conn = get_conn()
        try:
            rows = get_prices(conn, symbol)
            if not rows or len(rows) < 20:
                return {"error": "Not enough data"}
            return compute_indicators(rows)
        finally:
            _safe_close(conn)
    except Exception as exc:
        _database_http_error(exc)


@app.get("/buy/{symbol}")
def buy_signal(symbol: str):
    try:
        conn = get_conn()
        try:
            rows = get_prices(conn, symbol)
            if not rows or len(rows) < 20:
                return {"error": "Not enough data"}

            indicators = compute_indicators(rows)
            signal = check_buy_zone(conn, symbol, indicators, rows=rows)
            return {"symbol": symbol, "price": indicators.get("price"), "signal": signal}
        finally:
            _safe_close(conn)
    except Exception as exc:
        _database_http_error(exc)


@app.post("/telegram/test")
def telegram_test(payload: dict = Body(default=None)):
    message = None
    if isinstance(payload, dict):
        raw_message = payload.get("message")
        if isinstance(raw_message, str):
            message = raw_message.strip()

    if not message:
        message = f"Goldbot test ping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        telegram_response = send_telegram_message(message)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"ok": True, "message": message, "telegram_ok": telegram_response.get("ok", False)}


@app.websocket("/ws/market")
async def market_socket(websocket: WebSocket):
    await websocket.accept()
    focus_symbol = SYMBOLS[0] if SYMBOLS else None

    try:
        while True:
            try:
                raw_message = await asyncio.wait_for(websocket.receive_text(), timeout=STREAM_INTERVAL_SECONDS)
                message = json.loads(raw_message)
                if message.get("type") == "focus" and message.get("symbol") in SYMBOLS:
                    focus_symbol = message["symbol"]
            except asyncio.TimeoutError:
                pass

            try:
                frame = build_market_frame(focus_symbol)
            except Exception as exc:
                frame = {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "error": f"Market data is unavailable: {exc}",
                    "bot_health": read_runtime_status(),
                }
            await websocket.send_json(frame)
    except WebSocketDisconnect:
        return
