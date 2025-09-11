# app/models.py

from sqlalchemy import Column, Integer, String, Float
from .database import Base # Importamos la Base declarativa

class Movie(Base):
    """
    Este es el modelo de SQLAlchemy que representa la tabla 'movies' en la base de datos.
    Cada atributo de esta clase corresponde a una columna en la tabla.
    """
    __tablename__ = "movies"

    # Columnas de la tabla
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    categoria = Column(String)
    ano = Column(Integer) # Usamos 'ano' en lugar de 'año' por buenas prácticas
    director = Column(String)
    duracion = Column(Integer) # Duración en minutos
    calificacion = Column(Float)