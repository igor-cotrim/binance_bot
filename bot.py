import time
from datetime import datetime

import requests

from config import CHAT_ID, CHECK_INTERVAL, TELEGRAM_BOT_TOKEN


class BinanceListingsBot:
    def __init__(self):
        self.telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        self.binance_api = "https://api.binance.com/api/v3/exchangeInfo"
        self.previous_symbols = set()

    def get_current_listings(self):
        """Get a list of symbols listed on Binance"""
        try:
            response = requests.get(self.binance_api, timeout=10)
            response.raise_for_status()
            data = response.json()
            symbols = {s["symbol"] for s in data.get("symbols", [])}
            return symbols
        except Exception as e:
            print(f"❌ Error retrieving listings: {e}")
            return set()

    def send_message(self, text: str):
        """Send a message via Telegram"""
        try:
            params = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
            }
            url = f"{self.telegram_api}/sendMessage"
            requests.post(url, json=params, timeout=10)
            print("✅ Message sent successfully!")
        except Exception as e:
            print(f"❌ Error sending message: {e}")

    def format_message(self, new_symbols):
        """Format the message with the new symbols"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        symbols_list = "\n".join(
            [f"• <code>{s}</code>" for s in sorted(new_symbols)[:10]]
        )

        message = f"""
<b>🚀 New Coins Listed on Binance</b>

<b>Timestamp:</b> {timestamp}

<b>New Pairs ({len(new_symbols)}):</b>
{symbols_list}
"""
        if len(new_symbols) > 10:
            message += f"\n<i>...and {len(new_symbols) - 10} more pairs</i>"

        return message

    def run(self):
        """Main bot loop"""
        print("🤖 Bot started! Monitoring Binance...")
        print(f"⏱️ Checking every {CHECK_INTERVAL} seconds")

        initial_symbols = self.get_current_listings()
        self.previous_symbols = initial_symbols
        print(f"✅ Base established with {len(initial_symbols)} symbols")

        while True:
            try:
                current_symbols = self.get_current_listings()

                if not current_symbols:
                    time.sleep(CHECK_INTERVAL)
                    continue

                new_symbols = current_symbols - self.previous_symbols

                if new_symbols:
                    print(f"\n🎉 {len(new_symbols)} new listing(s) found!")
                    message = self.format_message(new_symbols)
                    self.send_message(message)
                    self.previous_symbols = current_symbols
                else:
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] No new listings"
                    )

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    bot = BinanceListingsBot()
    bot.run()
