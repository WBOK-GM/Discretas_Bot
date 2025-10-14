# Usamos la misma imagen base
FROM python:3.13-slim

WORKDIR /app

# Copiamos SOLO el archivo de requerimientos del Worker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del Worker
COPY . .
