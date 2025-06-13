from flask import Flask, request
from pybit.unified_trading import HTTP
import requests
import os

app = Flask(__name__)

# 📩 Configuración de Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ⚙️ Configuración de Bybit
API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
PERCENT_CAPITAL = float(os.getenv("CAPITAL_PERCENT", 10))  # Por defecto 10%
LEVERAGE = int(os.getenv("LEVERAGE", 20))  # Por defecto 20x

# 🧠 Inicializar sesión en Bybit
session = HTTP(
    testnet=False,  # True si estás en testnet
    api_key=API_KEY,
    api_secret=API_SECRET
)

@app.route("/")
def home():
    return "✅ Bot activo y corriendo."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📥 Alerta recibida:", data)

    # Extraer mensaje de alerta de TradingView
    alert = str(data.get("alert", "")).lower()

    if "btc" in alert:
        symbol = "BTCUSDT"
    elif "eth" in alert:
        symbol = "ETHUSDT"
    elif "sol" in alert:
        symbol = "SOLUSDT"
    else:
        return {"status": "symbol not supported"}, 400

    if "buy" in alert:
        side = "Buy"
    elif "sell" in alert:
        side = "Sell"
    else:
        return {"status": "side not recognized"}, 400

    # Obtener balance de USDT
    balance_info = session.get_wallet_balance(accountType="UNIFIED")
    usdt_balance = float(balance_info["result"]["list"][0]["totalEquity"])
    amount_to_use = usdt_balance * (PERCENT_CAPITAL / 100)

    # Obtener precio actual
    price_data = session.get_ticker(category="linear", symbol=symbol)
    price = float(price_data["result"]["list"][0]["lastPrice"])
    qty = round((amount_to_use * LEVERAGE) / price, 3)

    # Establecer apalancamiento
    session.set_leverage(category="linear", symbol=symbol, buyLeverage=LEVERAGE, sellLeverage=LEVERAGE)

    # Ejecutar orden de mercado
    order = session.place_order(
        category="linear",
        symbol=symbol,
        side=side,
        orderType="Market",
        qty=qty,
        timeInForce="GoodTillCancel"
    )

    # Enviar mensaje a Telegram
    mensaje = f"✅ Operación ejecutada:\n🪙 Par: {symbol}\n📈 Tipo: {side}\n📊 Cantidad: {qty} ({PERCENT_CAPITAL}% capital, {LEVERAGE}x)"
    send_telegram_message(mensaje)

    return {"status": "operación ejecutada"}, 200

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Error enviando a Telegram:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
