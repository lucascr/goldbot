# Web

The `web/` app is a FastAPI dashboard for browsing stored market data.

## Features

- Dashboard landing page at `/`
- Overview board for tracked symbols
- Detailed symbol snapshot endpoint
- Live WebSocket updates at `/ws/market`
- Bot health panel with runtime status
- Multi-timeframe signal display
- Telegram bot test panel
- Stale-data warnings on cards and detail views

## Telegram Test Panel

The dashboard includes a Telegram test section that sends a message using the shared bot config.

Before using it:

1. Set `TELEGRAM_TOKEN` and `CHAT_ID` in `bot/config_local.py` or environment variables.
2. Make sure the bot has already received a message from that chat.
3. For channels and supergroups, use the full `-100...` chat id.

If the panel shows `chat not found`, the bot token is valid but the configured `CHAT_ID` is not.

## Setup

1. Install dependencies:
   `pip install -r web/requirements.txt`
2. Make sure MySQL is running and `bot/config_local.py` or environment variables contain valid settings.
3. Make sure the bot has already collected some price history for indicators.

## Run

From the repository root:

`uvicorn web.api:app --host 0.0.0.0 --port 8009`

Then open:

`http://127.0.0.1:8009/`

## Main Files

- `web/api.py` FastAPI routes and WebSocket stream
- `web/dashboard.py` HTML renderer for the dashboard template
- `web/templates/dashboard.html` dashboard markup
- `web/static/dashboard.css` dashboard styling
- `web/static/dashboard.js` dashboard behavior
- `web/indicators.py` moving averages and RSI history
- `web/buy_signals.py` multi-timeframe signal logic
