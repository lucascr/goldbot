import json
from datetime import datetime, timezone
from pathlib import Path


STATUS_PATH = Path(__file__).resolve().parent.parent / "runtime" / "bot_status.json"


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_runtime_status():
    if not STATUS_PATH.exists():
        return {
            "status": "idle",
            "updated_at": None,
            "last_loop_at": None,
            "last_price_save_at": None,
            "last_telegram_at": None,
            "last_symbol": None,
            "last_price": None,
            "last_error": None,
        }

    try:
        return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {
            "status": "unknown",
            "updated_at": None,
            "last_loop_at": None,
            "last_price_save_at": None,
            "last_telegram_at": None,
            "last_symbol": None,
            "last_price": None,
            "last_error": "Could not read runtime status.",
        }


def update_runtime_status(**updates):
    status = read_runtime_status()
    status.update(updates)
    status["updated_at"] = utc_now_iso()

    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = STATUS_PATH.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    tmp_path.replace(STATUS_PATH)
    return status
