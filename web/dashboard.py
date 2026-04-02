import json
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "dashboard.html"


def render_dashboard(symbols, symbol_metadata):
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    bootstrap_json = json.dumps({"symbols": symbols, "symbolMeta": symbol_metadata})
    return html.replace("__BOOTSTRAP_JSON__", bootstrap_json)
