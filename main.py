from flask import Flask, request, render_template
import os
import requests

app = Flask(__name__)

# Lista para guardar los logs en memoria
logs = []

# Leer variables de entorno para Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Error al enviar mensaje a Telegram: {e}")

@app.route("/")
def home():
    return render_template("monitor.html", logs=logs)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logs.append(data)
    
    # Enviar mensaje a Telegram con formato bonito
    pair = data.get("PAIR", "N/A")
    side = data.get("SIDE", "N/A")
    message = f"📈 Señal recibida:\nPAIR: {pair}\nSIDE: {side}"
    send_telegram_message(message)

    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(debug=True)
