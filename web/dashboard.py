import json
from pathlib import Path


TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "dashboard.html"
V2_TEMPLATE_PATH = Path(__file__).resolve().parent / "version2" / "templates" / "dashboard.html"

def _render_template(template_path, symbols, symbol_metadata, rule_summary=None):
    html = template_path.read_text(encoding="utf-8")
    bootstrap_json = json.dumps(
        {
            "symbols": symbols,
            "symbolMeta": symbol_metadata,
            "ruleSummary": rule_summary or {},
        }
    )
    return html.replace("__BOOTSTRAP_JSON__", bootstrap_json)


def render_dashboard(symbols, symbol_metadata, rule_summary=None):
    return _render_template(TEMPLATE_PATH, symbols, symbol_metadata, rule_summary)


def render_dashboard_v2(symbols, symbol_metadata, rule_summary=None):
    return _render_template(V2_TEMPLATE_PATH, symbols, symbol_metadata, rule_summary)
