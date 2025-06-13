# Usa la imagen oficial de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos primero para cachear la instalación
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

# Expone el puerto 10000 (el mismo que usa tu app)
EXPOSE 10000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "main:app", "--workers", "2", "--timeout", "60", "--bind", "0.0.0.0:10000"]
