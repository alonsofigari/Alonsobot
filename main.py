from flask import Flask, request, jsonify
import os
import json
from bybit import HTTP
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variables de entorno
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", 20))
DEFAULT_CAPITAL_PERCENT = float(os.getenv("CAPITAL_PERCENT", 0.10))

# Cliente Bybit
session = HTTP(
    endpoint="https://api.bybit.com",
    api_key=API_KEY,
    api_secret=API_SECRET
)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

@app.route('/')
def home():
    return "🚀 Bot de Trading conectado correctamente."

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print(f"🔔 Alerta recibida: {data}")

        pair = data.get("pair", "").upper()
        side = data.get("side", "").upper()

        if pair not in SYMBOLS:
            return jsonify({"error": "Par no soportado."}), 400

        if side not in ["BUY", "SELL"]:
            return jsonify({"error": "Dirección no válida (usar BUY o SELL)."}), 400

        # Consulta saldo
        wallet = session.get_wallet_balance(coin="USDT")
        balance = float(wallet["result"]["USDT"]["available_balance"])
        amount_usdt = balance * DEFAULT_CAPITAL_PERCENT

        # Precio de mercado
        ticker = session.latest_information_for_symbol(symbol=pair)
        price = float(ticker["result"][0]["last_price"])
        qty = round((amount_usdt * DEFAULT_LEVERAGE) / price, 3)

        # Establecer apalancamiento
        session.set_leverage(symbol=pair, buy_leverage=DEFAULT_LEVERAGE, sell_leverage=DEFAULT_LEVERAGE)

        # Crear orden
        order = session.place_active_order(
            symbol=pair,
            side=side,
            order_type="Market",
            qty=qty,
            time_in_force="GoodTillCancel",
            reduce_only=False,
            close_on_trigger=False
        )

        print(f"✅ Orden ejecutada: {order}")
        return jsonify({"status": "ok", "order": order}), 200

    except Exception as e:
        print(f"❌ Error procesando alerta: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
