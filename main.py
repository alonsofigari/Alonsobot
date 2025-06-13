from flask import Flask, request
import requests
import os
from bybit import bybit

app = Flask(__name__)

# ✅ CONFIGURACIONES PRINCIPALES DESDE VARIABLES DE ENTORNO
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "TU_TOKEN_DEL_BOT")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "TU_CHAT_ID")
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "TU_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "TU_SECRET")

# ⚙️ AJUSTES DE TRADING (modificables desde Render)
TRADE_PERCENTAGE = float(os.getenv("TRADE_PERCENTAGE", 0.10))  # 10% capital por operación
LEVERAGE = int(os.getenv("LEVERAGE", 20))                      # Apalancamiento 20x

# 🌐 CONEXIÓN BYBIT
session = bybit(test=False, api_key=BYBIT_API_KEY, api_secret=BYBIT_API_SECRET)

@app.route("/")
def home():
    return "🚀 Bot corriendo correctamente."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Señal recibida:", data)

    mensaje = f"📈 Señal recibida:\n{data}"
    send_telegram_message(mensaje)

    try:
        symbol = data.get("symbol", "BTCUSDT")
        action = data.get("action", "BUY").upper()  # "BUY" o "SELL"

        # Obtener balance disponible
        balance = session.Wallet.Wallet_getBalance(coin="USDT").result()[0]["available_balance"]
        amount = round((balance * TRADE_PERCENTAGE) * LEVERAGE, 2)

        # Establecer apalancamiento
        session.Positions.Positions_saveLeverage(symbol=symbol, leverage=LEVERAGE).result()

        # Ejecutar orden de mercado
        side = "Buy" if action == "BUY" else "Sell"
        order = session.Order.Order_new(
            symbol=symbol,
            side=side,
            order_type="Market",
            qty=amount,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        ).result()

        send_telegram_message(f"✅ Orden ejecutada: {side} {symbol} x {amount} USDT con {LEVERAGE}x")
    except Exception as e:
        send_telegram_message(f"⚠️ Error al ejecutar orden: {str(e)}")

    return {"status": "ok"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Error enviando a Telegram:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
