#!/bin/bash
echo "Pasando variables al contenedor..."
export $(cat /etc/secrets/render-env | xargs)
echo "Iniciando bot..."
exec /usr/bin/docker run -p $PORT:8000 alonso_bybit_bot
