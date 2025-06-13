from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os
import logging

# Configurar logging profesional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurar cliente Bybit CORRECTO
session = HTTP(
    api_key=os.getenv("BYBIT_API_KEY"),
    api_secret=os.getenv("BYBIT_API_SECRET"),
    testnet=False,  # Cambia a True si estás en testnet
    recv_window=5000
)

# Normalizar nombres de pares
SYMBOL_MAP = {
    "BTCUSDT": "BTCUSDT",
    "ETHUSDT": "ETHUSDT",
    "SOLUSDT": "SOLUSDT",
    # Agrega otros pares que uses
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    logger.info(f"Alerta recibida: {data}")

    try:
        # Normalizar datos de entrada
        pair = SYMBOL_MAP.get((data.get("pair") or "").upper().replace("/", ""))
        side = (data.get("side") or "").capitalize()  # Convierte "buy" -> "Buy"
        
        if not pair or pair not in SYMBOL_MAP:
            return jsonify({"error": f"Par no válido: {data.get('pair')}"}), 400
            
        if side not in ["Buy", "Sell"]:
            return jsonify({"error": f"Lado no válido: {data.get('side')}"}), 400

        # Obtener precio CORRECTO
        price_data = session.get_orderbook(category="linear", symbol=pair)
        current_price = float(price_data["result"]["list"][0]["ask1Price"])
        
        # Obtener balance CORRECTO (nueva estructura V5)
        balance = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        usdt_balance = float(balance["result"]["list"][0]["coin"][0]["availableToTrade"])
        
        # ... (resto del cálculo de cantidad) ...

        # Verificar apalancamiento ANTES de operar
        leverage_response = session.set_leverage(
            category="linear",
            symbol=pair,
            buyLeverage=20,
            sellLeverage=20
        )
        logger.info(f"Leverage response: {leverage_response}")

        # Enviar orden CON LOGGING
        order = session.place_order(
            category="linear",
            symbol=pair,
            side=side,  # Ahora "Buy" con mayúscula
            orderType="Market",
            qty=0.001,  # Usa valor fijo para pruebas
            timeInForce="GoodTillCancel"
        )
        logger.info(f"Respuesta Bybit: {order}")

        # Enviar mensaje a Telegram (agrega tu lógica aquí)

        return jsonify({"message": "Orden ejecutada", "order": order["result"]})

    except Exception as e:
        logger.exception("Error crítico:")  # Log detallado
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Configuración para producción
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, threaded=True)
