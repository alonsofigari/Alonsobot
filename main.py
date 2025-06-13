from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os

# Inicializar la app Flask
app = Flask(__name__)

# Obtener claves desde variables de entorno
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")

# Cliente de Bybit
session = HTTP(
    api_key=API_KEY,
    api_secret=API_SECRET,
)

# Configuración por defecto
DEFAULT_LEVERAGE = 20
DEFAULT_CAPITAL_PERCENT = 0.10

# Tamaños mínimos de contratos por símbolo
MIN_TRADE_QTY = {
    "BTCUSDT": 0.001,
    "ETHUSDT": 0.01,
    "SOLUSDT": 0.1,
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Alerta recibida:", data)

    try:
        pair = data.get("pair") or data.get("PAIR")
        side = data.get("side") or data.get("SIDE")

        if not pair or not side:
            return jsonify({"error": "Faltan campos obligatorios (pair o side)."}), 400

        # Obtener precio de mercado actual
        price_data = session.get_orderbook(category="linear", symbol=pair, limit=1)
        current_price = float(price_data["result"]["list"][0]["price"])

        # Obtener balance disponible
        balance_data = session.get_wallet_balance(accountType="UNIFIED")
        usdt_balance = float(balance_data["result"]["list"][0]["coin"][0]["availableToTrade"])

        # Calcular cantidad de la orden
        capital_to_use = usdt_balance * DEFAULT_CAPITAL_PERCENT
        qty = round((capital_to_use * DEFAULT_LEVERAGE) / current_price, 3)

        # Asegurar mínimo
        min_qty = MIN_TRADE_QTY.get(pair.upper(), 0.01)
        if qty < min_qty:
            qty = min_qty

        # Cancelar órdenes previas
        session.cancel_all_orders(category="linear", symbol=pair)

        # Establecer apalancamiento
        session.set_leverage(
            category="linear",
            symbol=pair,
            buyLeverage=DEFAULT_LEVERAGE,
            sellLeverage=DEFAULT_LEVERAGE
        )

        # Colocar orden
        order = session.place_order(
            category="linear",
            symbol=pair,
            side=side.upper(),
            orderType="Market",
            qty=qty,
            timeInForce="GoodTillCancel",
            reduceOnly=False
        )

        return jsonify({"message": "Orden enviada", "detalle": order})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "🚀 Bot operativo - Conectado a Bybit y escuchando señales de TradingView"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
