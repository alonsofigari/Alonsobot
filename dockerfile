FROM python:3.10-bullseye  # Imagen más completa

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["gunicorn", "main:app", "--workers", "1", "--timeout", "90", "--bind", "0.0.0.0:10000"]
RUN pip install --no-cache-dir pybit==2.3.1 --no-binary :all:
