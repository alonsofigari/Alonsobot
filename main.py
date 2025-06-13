from flask import Flask, request
import requests
import os

print("🔐 TELEGRAM_BOT_TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("💬 TELEGRAM_CHAT_ID:", os.getenv("TELEGRAM_CHAT_ID"))
print("🔑 BYBIT_API_KEY:", os.getenv("BYBIT_API_KEY"))
print("🗝️ BYBIT_API_SECRET:", os.getenv("BYBIT_API_SECRET"))
from pybit import HTTP

app = Flask(__name__)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Bybit API real
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
session = HTTP("https://api.bybit.com", api_key=API_KEY, api_secret=API_SECRET)

# Configuración predeterminada
DEFAULT_LEVERAGE = 20
CAPITAL_PERCENTAGE = 0.10

@app.route("/")
def home():
    return "Servidor activo y conectado a Bybit."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Señal recibida:", data)

    symbol = data.get("PAIR")
    side = data.get("SIDE")  # "BUY" o "SELL"
    if not symbol or not side:
        return {"status": "error", "message": "Datos incompletos"}, 400

    # Formato en Bybit: BTC/USDT → BTCUSDT
    symbol = symbol.replace("-", "")

    position_side = "Buy" if side == "BUY" else "Sell"
    close_side = "Sell" if side == "BUY" else "Buy"

    try:
        balance = session.get_wallet_balance(coin="USDT")["result"]["USDT"]["available_balance"]
        order_value = round(balance * CAPITAL_PERCENTAGE, 2)

        # Obtener precio actual del mercado
        price_data = session.latest_information_for_symbol(symbol=symbol)["result"][0]
        mark_price = float(price_data["mark_price"])
        qty = round((order_value * DEFAULT_LEVERAGE) / mark_price, 3)

        # Establecer apalancamiento
        session.set_leverage(symbol=symbol, buy_leverage=DEFAULT_LEVERAGE, sell_leverage=DEFAULT_LEVERAGE)

        # Abrir orden de mercado
        order = session.place_active_order(
            symbol=symbol,
            side=position_side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )

        # Enviar alerta a Telegram
        send_telegram_message(f"✅ Orden ejecutada:\nSímbolo: {symbol}\nDirección: {position_side}\nTamaño: {qty} ({CAPITAL_PERCENTAGE*100}% del capital)")

    except Exception as e:
        print("Error:", e)
        send_telegram_message(f"❌ Error al ejecutar orden:\n{e}")
        return {"status": "error", "message": str(e)}, 500

    return {"status": "success"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
