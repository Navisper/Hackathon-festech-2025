# Imagen base
FROM python:3.13-slim

# Crear directorio de la app
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la app
COPY . .

# Exponer puerto 10000
EXPOSE 10000

# Comando para iniciar FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
