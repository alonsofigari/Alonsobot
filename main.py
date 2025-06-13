from flask import Flask, request
import requests
import os
from pybit.unified_trading import HTTP

app = Flask(__name__)

# Telegram config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7754651648:AAFUzgIPhm6SbFg9Q_0rQbodYRQ_db0O3Mc")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "479067462")

# Bybit API credentials
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "TU_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "TU_API_SECRET")

# Bybit connection
bybit_client = HTTP(
    api_key=BYBIT_API_KEY,
    api_secret=BYBIT_API_SECRET,
)

@app.route("/")
def home():
    return "Bot corriendo correctamente."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Recibido:", data)

    # Enviar a Telegram
    message = f"📢 Alerta recibida:\n{data}"
    send_telegram_message(message)

    # Procesar alerta y ejecutar orden si aplica
    try:
        process_alert(data)
    except Exception as e:
        print("Error procesando alerta:", e)

    return {"status": "ok"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error enviando a Telegram:", e)

def process_alert(data):
    signal = str(data).lower()

    if "long" in signal:
        # Ejecutar compra
        print("Ejecutando orden de COMPRA en Bybit")
        bybit_client.place_order(
            category="linear",
            symbol="BTCUSDT",
            side="Buy",
            order_type="Market",
            qty=0.01,
            time_in_force="GoodTillCancel",
        )

    elif "short" in signal:
        # Ejecutar venta
        print("Ejecutando orden de VENTA en Bybit")
        bybit_client.place_order(
            category="linear",
            symbol="BTCUSDT",
            side="Sell",
            order_type="Market",
            qty=0.01,
            time_in_force="GoodTillCancel",
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
