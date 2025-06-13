from flask import Flask, request
import requests
import os

# 👇 Imprime para verificar que las variables se están leyendo correctamente (solo para pruebas)
print("🔐 TELEGRAM_BOT_TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("💬 TELEGRAM_CHAT_ID:", os.getenv("TELEGRAM_CHAT_ID"))
print("🔑 BYBIT_API_KEY:", os.getenv("BYBIT_API_KEY"))
print("🗝️ BYBIT_API_SECRET:", os.getenv("BYBIT_API_SECRET"))

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

@app.route("/")
def home():
    return "✅ Bot corriendo correctamente."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📥 Alerta recibida:", data)

    # Procesar mensaje de TradingView
    symbol = data.get("PIR") or data.get("SYMBOL")
    side = data.get("SIDE") or data.get("SIGNAL")

    message = f"📢 Señal recibida\n🔹Par: {symbol}\n📈 Dirección: {side}"
    send_telegram_message(message)

    # Aquí en el futuro se conectará con Bybit para ejecutar órdenes

    return {"status": "ok"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        response = requests.post(url, data=payload)
        print("✅ Enviado a Telegram")
    except Exception as e:
        print("❌ Error enviando a Telegram:", e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
