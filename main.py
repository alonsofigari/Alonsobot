from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "7754651648:AAFUzgIPhm6SbFg9Q_0rQbodYRQ_db0O3Mc"
TELEGRAM_CHAT_ID = "479067462"

@app.route("/")
def home():
    return "Bot corriendo correctamente."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Recibido:", data)

    message = f"📢 Alerta recibida:\n{data}"
    send_telegram_message(message)

    return {"status": "ok"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Error enviando a Telegram:", e)

if __name__ == "__main__":
    app.run(debug=True)
