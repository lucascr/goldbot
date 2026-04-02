# Bot

The `bot/` app is the market collector and Telegram alert worker.

## What It Does

- Fetches prices from Yahoo Finance for the configured symbols
- Stores prices in MySQL
- Evaluates alert rules
- Sends Telegram messages when conditions are met

## Setup

1. Install dependencies:
   `pip install -r bot/requirements.txt`
2. Create the database:
   `CREATE DATABASE goldbot;`
3. Apply the schema:
   `mysql -u root -p goldbot < bot/schema.sql`
4. Copy `bot/config.sample.py` to `bot/config_local.py`.
5. Update `bot/config_local.py` with your database and Telegram settings.

You can also override config with environment variables:

- `GOLDBOT_DB_HOST`
- `GOLDBOT_DB_USER`
- `GOLDBOT_DB_PASSWORD`
- `GOLDBOT_DB_NAME`
- `GOLDBOT_TELEGRAM_TOKEN`
- `GOLDBOT_CHAT_ID`
- `GOLDBOT_CHECK_INTERVAL`

## Telegram Setup

1. Create the bot in BotFather.
2. Set `TELEGRAM_TOKEN` in `bot/config_local.py`.
3. Start a conversation with the bot, or add it to the target group or channel.
4. Send a message to generate an update.
5. Open:
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
6. Copy the returned `chat.id` into `CHAT_ID`.

Important:

- Personal chats usually have a positive id.
- Groups, supergroups, and channels usually have a negative id.
- For channels and many supergroups, use the full `-100...` id exactly as returned.
- If you get `{"ok":true,"result":[]}`, send the bot a message first.
- If you get `Bad Request: chat not found`, the bot does not have access to that chat id yet.

## Run

From the repository root:

`python -m bot.bot`

## Important Files

- `bot/bot.py` main loop
- `bot/config.py` shared defaults and config loader
- `bot/config.sample.py` config template
- `bot/config_local.py` local ignored secrets
- `bot/db.py` database access
- `bot/strategy.py` alert rules
- `bot/telegram.py` Telegram sender
- `bot/schema.sql` schema
