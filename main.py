from flask import Flask, request, render_template
import os
import json
from datetime import datetime

app = Flask(__name__)

# Estado del bot (simulado)
bot_status = {
    "status": "Activo",
    "last_action": "Esperando señal",
    "last_pair": "BTC/USDT",
    "last_side": "N/A",
    "entry_price": None,
    "trailing_stop": None,
    "trailing_active": False
}

log_file = "bot_activity.log"

# Función para guardar logs
def guardar_log(mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {mensaje}\n")

@app.route("/")
def panel():
    # Mostrar últimos 30 logs
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.readlines()[-30:]
    else:
        logs = ["Sin registros aún."]

    return render_template("monitor.html", status=bot_status, logs=logs)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    pair = data.get("pair")
    side = data.get("side")
    price = float(data.get("price", 0))

    bot_status["last_pair"] = pair
    bot_status["last_side"] = side
    bot_status["entry_price"] = price
    bot_status["last_action"] = f"{side.upper()} {pair} @ {price}"
    bot_status["trailing_active"] = True
    bot_status["trailing_stop"] = price * 0.98 if side.lower() == "long" else price * 1.02

    guardar_log(f"Señal recibida: {side.upper()} {pair} @ {price}")
    guardar_log(f"Trailing activado en: {bot_status['trailing_stop']:.2f}")

    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
