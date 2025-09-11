# app/config.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    """
    Clase para gestionar la configuración de la aplicación.
    Pydantic se encarga automáticamente de leer las variables
    del archivo .env y del entorno del sistema.
    """
    database_url: str

    class Config:
        # Le dice a Pydantic que busque un archivo .env
        env_file = ".env"

# Creamos una instancia de la configuración que usaremos en toda la app
settings = Settings()