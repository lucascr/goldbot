import pandas as pd


def _build_dataframe(rows):
    if not rows:
        return pd.DataFrame(columns=["price", "timestamp"])

    df = pd.DataFrame(rows)
    df.columns = ["price", "timestamp"]
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["price"] = df["price"].astype(float)
    df = df.sort_values("timestamp")

    df["ma20"] = df["price"].rolling(20).mean()
    df["ma50"] = df["price"].rolling(50).mean()

    delta = df["price"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    loss = loss.replace(0, 1e-10)

    rs = gain / loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def build_indicator_history(rows):
    df = _build_dataframe(rows)
    history = []

    for _, row in df.iterrows():
        history.append(
            {
                "price": float(row["price"]) if not pd.isna(row["price"]) else None,
                "timestamp": row["timestamp"].isoformat() if not pd.isna(row["timestamp"]) else None,
                "ma20": float(row["ma20"]) if not pd.isna(row["ma20"]) else None,
                "ma50": float(row["ma50"]) if not pd.isna(row["ma50"]) else None,
                "rsi": float(row["rsi"]) if not pd.isna(row["rsi"]) else None,
            }
        )

    return history


def compute_indicators(rows):
    history = build_indicator_history(rows)
    if len(history) < 20:
        return {}

    last = history[-1]
    return {
        "price": last["price"],
        "ma20": last["ma20"],
        "ma50": last["ma50"],
        "rsi": last["rsi"],
    }
