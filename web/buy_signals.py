from datetime import timedelta

TIMEFRAMES = (
    {"key": "15m", "minutes": 15, "drop_threshold": -0.008},
    {"key": "30m", "minutes": 30, "drop_threshold": -0.015},
    {"key": "1h", "minutes": 60, "drop_threshold": -0.022},
    {"key": "4h", "minutes": 240, "drop_threshold": -0.035},
)


def _normalize_rows(rows):
    normalized = []
    for price, timestamp in rows or []:
        if timestamp is None:
            continue
        normalized.append((float(price), timestamp))
    normalized.sort(key=lambda item: item[1])
    return normalized


def _window_change(rows, minutes):
    normalized = _normalize_rows(rows)
    if len(normalized) < 2:
        return None

    latest_ts = normalized[-1][1]
    cutoff = latest_ts - timedelta(minutes=minutes)
    window = [item for item in normalized if item[1] >= cutoff]

    if len(window) < 2:
        return None

    oldest_price = window[0][0]
    latest_price = window[-1][0]
    if oldest_price == 0:
        return None

    return (latest_price - oldest_price) / oldest_price


def _build_reasons(price, ma20, rsi, change, drop_threshold):
    reasons = []

    if rsi is not None and rsi < 35:
        reasons.append("RSI_OVERSOLD")

    if change is not None and change <= drop_threshold:
        reasons.append("FAST_DROP")

    if ma20 is not None and price is not None and price < ma20:
        reasons.append("BELOW_MA20")

    return reasons


def analyze_multi_timeframes(rows, indicators):
    if not indicators:
        return []

    price = float(indicators["price"]) if indicators.get("price") is not None else None
    ma20 = float(indicators["ma20"]) if indicators.get("ma20") is not None else None
    rsi = float(indicators["rsi"]) if indicators.get("rsi") is not None else None

    signals = []
    for timeframe in TIMEFRAMES:
        change = _window_change(rows, timeframe["minutes"])
        reasons = _build_reasons(price, ma20, rsi, change, timeframe["drop_threshold"])
        confidence = len(reasons)

        signals.append(
            {
                "timeframe": timeframe["key"],
                "minutes": timeframe["minutes"],
                "change": change,
                "signal": "BUY" if confidence >= 2 else None,
                "confidence": confidence,
                "reasons": reasons,
            }
        )

    return signals


def check_buy_zone(conn, symbol, indicators, rows=None):
    del conn, symbol

    timeframe_signals = analyze_multi_timeframes(rows or [], indicators)
    active = [item for item in timeframe_signals if item["signal"]]

    if not timeframe_signals:
        return None

    strongest = max(timeframe_signals, key=lambda item: (item["confidence"], item["minutes"]))

    return {
        "signal": "BUY" if active else None,
        "confidence": strongest["confidence"],
        "reasons": strongest["reasons"],
        "timeframes": timeframe_signals,
        "active_timeframes": [item["timeframe"] for item in active],
        "summary": "BUY" if active else "WAIT",
    }
