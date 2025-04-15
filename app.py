from flask import Flask, request
import requests
from config import ULTRAMSG_INSTANCE_ID, ULTRAMSG_TOKEN
from utils import get_binance_price, get_rsi_ema

app = Flask(__name__)

def send_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    data = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    requests.post(url, data=data)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    sender = data['data']['from']
    message = data['data']['body'].strip().lower()

    if "price" in message:
        symbol = message.replace("price", "").strip().upper() or "BTCUSDT"
        price = get_binance_price(symbol)
        send_message(sender, f"💰 Current price of {symbol}: ${price}")
    elif "signal" in message:
        symbol = "BTC/USDT"
        rsi, ema = get_rsi_ema(symbol)
        signal = "🔼 BUY" if rsi < 30 else "🔽 SELL" if rsi > 70 else "⏸️ WAIT"
        send_message(sender, f"📊 Signal for {symbol}\nRSI: {rsi}\nEMA: {ema}\nRecommendation: {signal}")
    else:
        send_message(sender, "👋 Welcome to Crypto Bot! Send:\n- `price BTCUSDT`\n- `signal`")

    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
