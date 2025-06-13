from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os
import logging
import time
import requests  # Para enviar mensajes a Telegram

# Configuración profesional de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BYBIT_BOT")

app = Flask(__name__)

# Configuración segura de Bybit (CUENTA REAL)
def get_bybit_session():
    return HTTP(
        api_key=os.getenv("BYBIT_API_KEY"),
        api_secret=os.getenv("BYBIT_API_SECRET"),
        testnet=False,  # IMPORTANTE: False para cuenta real
        recv_window=5000
    )

# Tamaños mínimos de contratos
MIN_TRADE_QTY = {
    "BTCUSDT": 0.001,
    "ETHUSDT": 0.01,
    "SOLUSDT": 0.1
}

# Función para enviar a Telegram
def send_telegram_alert(message: str):
    """Envía mensajes a Telegram a través de tu bot"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.error("Faltan credenciales de Telegram")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.error(f"Error Telegram: {response.text}")
    except Exception as e:
        logger.error(f"Error enviando a Telegram: {str(e)}")

@app.route("/webhook", methods=["POST"])
def webhook():
    start_time = time.time()
    logger.info("Alerta recibida")
    
    try:
        # 1. Validar payload
        data = request.json
        if not data:
            send_telegram_alert("❌ Error: Payload vacío")
            return jsonify({"error": "Payload vacío"}), 400
            
        logger.info(f"Datos recibidos: {data}")
        
        # 2. Procesar parámetros
        pair = (data.get("pair") or "").strip().replace("/", "").replace(" ", "").upper()
        side = (data.get("side") or "").strip().capitalize()
        
        # Validación crítica para cuenta real
        if pair not in MIN_TRADE_QTY:
            error_msg = f"❌ Par inválido: {pair}. Pares válidos: {list(MIN_TRADE_QTY.keys())}"
            send_telegram_alert(error_msg)
            return jsonify({"error": error_msg}), 400
            
        if side not in ["Buy", "Sell"]:
            error_msg = f"❌ Side inválido: {side}. Use 'Buy' o 'Sell'"
            send_telegram_alert(error_msg)
            return jsonify({"error": error_msg}), 400
        
        # 3. Crear sesión de Bybit
        session = get_bybit_session()
        
        # 4. Obtener precio de mercado
        ticker = session.get_tickers(category="linear", symbol=pair)
        if not ticker or "result" not in ticker or not ticker["result"]["list"]:
            error_msg = f"❌ Error obteniendo precio para {pair}"
            send_telegram_alert(error_msg)
            return jsonify({"error": error_msg}), 500
            
        current_price = float(ticker["result"]["list"][0]["lastPrice"])
        
        # 5. Obtener balance
        balance = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        if not balance or "result" not in balance or not balance["result"]["list"]:
            error_msg = "❌ Error obteniendo balance"
            send_telegram_alert(error_msg)
            return jsonify({"error": error_msg}), 500
            
        usdt_balance = float(balance["result"]["list"][0]["coin"][0]["availableToTrade"])
        
        # 6. Calcular cantidad (con márgenes de seguridad)
        leverage = 20
        risk_percent = 0.10
        capital_to_risk = usdt_balance * risk_percent
        qty = (capital_to_risk * leverage) / current_price
        qty = round(max(qty, MIN_TRADE_QTY[pair]), 3)
        
        logger.info(f"Operación: {pair} | {side} | QTY: {qty} | Precio: {current_price}")
        
        # 7. Configurar apalancamiento
        leverage_res = session.set_leverage(
            category="linear",
            symbol=pair,
            buyLeverage=leverage,
            sellLeverage=leverage
        )
        logger.info(f"Respuesta apalancamiento: {leverage_res}")
        
        # 8. Enviar orden
        order_response = session.place_order(
            category="linear",
            symbol=pair,
            side=side,
            orderType="Market",
            qty=str(qty),  # Bybit requiere string
            timeInForce="GoodTillCancel"
        )
        
        # 9. Notificar resultados
        if order_response.get("retCode") != 0:
            error_msg = f"❌ Bybit error: {order_response.get('retMsg')}"
            send_telegram_alert(error_msg)
            return jsonify({"error": error_msg}), 500
            
        order_id = order_response["result"]["orderId"]
        msg = f"✅ ORDEN EJECUTADA: {side} {qty} {pair} | ID: {order_id}"
        logger.info(msg)
        send_telegram_alert(msg)
        
        # 10. Métricas de rendimiento
        process_time = round(time.time() - start_time, 2)
        logger.info(f"Proceso completado en {process_time}s")
        
        return jsonify({
            "status": "success",
            "order_id": order_id,
            "symbol": pair,
            "qty": qty,
            "process_time": process_time
        })
        
    except Exception as e:
        error_msg = f"🚨 ERROR CRÍTICO: {str(e)}"
        logger.exception(error_msg)
        send_telegram_alert(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route("/")
def home():
    return "🚀 Bot Operativo (Bybit + TradingView + Telegram)"

if __name__ == "__main__":
    # Solo para desarrollo local
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
