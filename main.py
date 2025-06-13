from flask import Flask, request
import requests
import os
from pybit.unified_trading import HTTP

app = Flask(__name__)

# Carga variables desde Render
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Conexión a Bybit (cuenta real)
session = HTTP(
    api_key=API_KEY,
    api_secret=API_SECRET
)

@app.route("/")
def home():
    return "Servidor funcionando."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Alerta recibida:", data)

    # Acepta keys minúsculas o mayúsculas
    pair = data.get("pair") or data.get("PAIR")
    side = data.get("side") or data.get("SIDE")

    if pair is None or side is None:
        return {"error": "Falta 'pair' o 'side'"}, 400

    # Configuración base
    leverage = float(os.getenv("LEVERAGE", 20))
    capital_pct = float(os.getenv("CAPITAL_PCT", 10))  # % del capital a usar
    pair = pair.upper()
    side = side.upper()

    # Obtener balance
    balance = session.get_wallet_balance(accountType="UNIFIED")["result"]["list"][0]["totalEquity"]
    amount_usdt = balance * (capital_pct / 100)

    # Obtener precio actual
    price_data = session.get_ticker(category="linear", symbol=pair)["result"]["list"][0]
    last_price = float(price_data["lastPrice"])

    # Calcular cantidad de contrato (qty)
    qty = round((amount_usdt * leverage) / last_price, 3)

    # Enviar orden
    order = session.place_order(
        category="linear",
        symbol=pair,
        side=side,
        orderType="Market",
        qty=qty,
        timeInForce="GoodTillCancel"
    )

    # Enviar a Telegram
    msg = f"📈 ORDEN ENVIADA:\nPAIR: {pair}\nSIDE: {side}\nQTY: {qty}\nPRICE: {last_price}"
    send_telegram_message(msg)

    return {"status": "ok"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error al enviar a Telegram:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
