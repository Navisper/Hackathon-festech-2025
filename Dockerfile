# Dockerfile

# 1. Usar una imagen base oficial de Python
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /code

# 3. Instalar dependencias para mantener la imagen ligera
COPY requirements.txt .
RUN pip install uv && uv pip install --system --no-cache -r requirements.txt

# 4. Copiar el código de la aplicación
COPY ./app /code/app

# 5. Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# 6. Comando para iniciar la aplicación cuando el contenedor se ejecute
# Se usa --host 0.0.0.0 para que la API sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]