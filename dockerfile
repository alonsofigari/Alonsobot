FROM python:3.9-slim

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y build-essential

# Copia e instala dependencias Python primero (para cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código
COPY . .

# Expone el puerto (debe ser 8000)
EXPOSE 8000

# Comando para ejecutar tu bot
CMD ["python", "-u", "alonso_bybit_bot.py"]
