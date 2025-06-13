from flask import Flask, request, jsonify
from pybit.unified_trading import HTTP
import os
import logging
import time
import requests

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
        testnet=False,
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
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        logger.error("Faltan credenciales de Telegram")
        return
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id
