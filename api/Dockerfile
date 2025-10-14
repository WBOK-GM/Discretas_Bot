# Usamos una imagen base de Python más ligera (slim)
FROM python:3.13-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos SOLO el archivo de requerimientos de la API
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la API al contenedor
COPY . .

# Exponemos el puerto que usará FastAPI
EXPOSE 8000
