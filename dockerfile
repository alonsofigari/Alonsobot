FROM python:3.9-slim-bullseye

WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código
COPY . .

# Puerto expuesto (¡DEBE ser 8000!)
EXPOSE 8000

# Comando de inicio
CMD ["python", "-u", "alonso_bybit_bot.py"]
