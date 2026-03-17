# 🤖 Crypto Listings Bot (Binance + Bybit)

A simple Python bot that monitors **newly listed trading pairs** and sends real-time notifications to your **Telegram** account.

## 🚀 Features

- Periodically fetches symbols from multiple exchanges:
  - Binance (`/api/v3/exchangeInfo`)
  - Bybit (`/v5/market/instruments-info?category=spot`)
- Detects newly listed trading pairs by comparing with the previous snapshot.
- Sends a formatted Telegram message containing:
  - Exchange name
  - Detection timestamp
  - List of new pairs
  - Count of how many new pairs were found
- Lets you choose which exchanges to monitor via config.

## 📁 Project Structure

```bash
binance_bot/
├── bot.py          # Core bot logic (Exchanges + Telegram)
├── main.py         # Entry point to run the bot
├── config.py       # Configuration (token, chat id, interval, exchanges)
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.8+
- A Telegram account
- A Telegram bot token (from @BotFather)
- Your Telegram Chat ID

## ⚙️ Setup

1. Create project folder and move into it:

```bash
mkdir binance_bot
cd binance_bot
```

2. (Optional but recommended) Create and activate a virtual environment:

```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure `config.py`:

```python
# config.py
TELEGRAM_BOT_TOKEN = "YOUR_BOTFATHER_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
CHECK_INTERVAL = 60  # seconds

# Optional: choose which exchanges to monitor
MONITORED_EXCHANGES = ["binance", "bybit"]
```

## 🤖 Getting the bot token (BotFather)

1. In Telegram, search for @BotFather.
2. Send /start, then /newbot.
3. Follow the instructions to choose:

- A display name
- A unique username (must end with `_bot`).

4. BotFather will return a token like:

```text
123456789:ABCdefGHIjklmnoPQRstuvwxyzABC
```

Copy this and put it into `TELEGRAM_BOT_TOKEN` in `config.py`.

## 👤 Getting your Telegram Chat ID

1. Open the chat with the bot you just created.
2. Click Start or send /start.
3. In your browser, go to:

```text
https://api.telegram.org/botYOUR_TOKEN_HERE/getUpdates
```

4. Look for the `chat` object in the JSON response:

```json
"chat": {
  "id": 987654321,
  "first_name": "Your Name",
  "type": "private"
}
```

The `id` value (`987654321` in this example) is your `CHAT_ID`.

## ▶️ Running the bot

To start the monitoring loop:

```bash
python main.py
# or
python3 main.py
```
