import time
from datetime import datetime

import requests

import config


CHAT_ID = config.CHAT_ID
CHECK_INTERVAL = config.CHECK_INTERVAL
TELEGRAM_BOT_TOKEN = config.TELEGRAM_BOT_TOKEN
MONITORED_EXCHANGES = getattr(
    config,
    "MONITORED_EXCHANGES",
    ["binance", "bybit"],
)


class ListingsBot:
    EXCHANGES = {
        "binance": {
            "label": "Binance",
            "url": "https://api.binance.com/api/v3/exchangeInfo",
            "extract": lambda data: {
                symbol["symbol"] for symbol in data.get("symbols", [])
            },
        },
        "bybit": {
            "label": "Bybit",
            "url": (
                "https://api.bybit.com/v5/market/instruments-info"
                "?category=spot&limit=1000"
            ),
            "extract": lambda data: {
                symbol["symbol"]
                for symbol in data.get("result", {}).get("list", [])
            },
        },
    }

    def __init__(self, exchanges=None):
        self.telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        selected_exchanges = exchanges or MONITORED_EXCHANGES
        self.exchanges = [exchange.lower() for exchange in selected_exchanges]
        self.previous_symbols = {exchange: set() for exchange in self.exchanges}

        invalid_exchanges = [
            exchange for exchange in self.exchanges if exchange not in self.EXCHANGES
        ]
        if invalid_exchanges:
            supported = ", ".join(sorted(self.EXCHANGES))
            invalid = ", ".join(sorted(invalid_exchanges))
            raise ValueError(
                f"Unsupported exchange(s): {invalid}. Supported exchanges: {supported}"
            )

    def get_current_listings(self, exchange):
        """Get a list of symbols listed on the selected exchange."""
        exchange_config = self.EXCHANGES[exchange]

        try:
            response = requests.get(exchange_config["url"], timeout=10)
            response.raise_for_status()
            data = response.json()
            return exchange_config["extract"](data)
        except Exception as error:
            print(f"❌ Error retrieving listings from {exchange}: {error}")
            return set()

    def send_message(self, text: str):
        """Send a message via Telegram."""
        try:
            params = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
            }
            url = f"{self.telegram_api}/sendMessage"
            requests.post(url, json=params, timeout=10)
            print("✅ Message sent successfully!")
        except Exception as error:
            print(f"❌ Error sending message: {error}")

    def format_message(self, exchange, new_symbols):
        """Format the message with the new symbols."""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        exchange_label = self.EXCHANGES[exchange]["label"]

        symbols_list = "\n".join(
            [f"• <code>{symbol}</code>" for symbol in sorted(new_symbols)[:10]]
        )

        message = f"""
<b>🚀 New Coins Listed on {exchange_label}</b>

<b>Timestamp:</b> {timestamp}

<b>New Pairs ({len(new_symbols)}):</b>
{symbols_list}
"""
        if len(new_symbols) > 10:
            message += f"\n<i>...and {len(new_symbols) - 10} more pairs</i>"

        return message

    def run(self):
        """Main bot loop."""
        exchange_labels = ", ".join(
            self.EXCHANGES[exchange]["label"] for exchange in self.exchanges
        )

        print(f"🤖 Bot started! Monitoring: {exchange_labels}")
        print(f"⏱️ Checking every {CHECK_INTERVAL} seconds")

        for exchange in self.exchanges:
            initial_symbols = self.get_current_listings(exchange)
            self.previous_symbols[exchange] = initial_symbols
            print(
                "✅ Base established for "
                f"{self.EXCHANGES[exchange]['label']} "
                f"with {len(initial_symbols)} symbols"
            )

        while True:
            try:
                for exchange in self.exchanges:
                    current_symbols = self.get_current_listings(exchange)

                    if not current_symbols:
                        continue

                    new_symbols = current_symbols - self.previous_symbols[exchange]

                    if new_symbols:
                        print(
                            f"\n🎉 {len(new_symbols)} new listing(s) found "
                            f"on {self.EXCHANGES[exchange]['label']}!"
                        )
                        message = self.format_message(exchange, new_symbols)
                        self.send_message(message)

                    self.previous_symbols[exchange] = current_symbols

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring cycle done")
                time.sleep(CHECK_INTERVAL)

            except Exception as error:
                print(f"❌ Error in main loop: {error}")
                time.sleep(CHECK_INTERVAL)


# Backward compatible name used by older imports.
BinanceListingsBot = ListingsBot


if __name__ == "__main__":
    bot = ListingsBot()
    bot.run()
