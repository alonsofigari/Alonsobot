FROM python:3.10-slim

# Instala compiladores necesarios
RUN apt-get update && apt-get install -y build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "main:app", "--workers", "1", "--timeout", "90", "--bind", "0.0.0.0:10000"]
