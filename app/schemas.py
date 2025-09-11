# app/schemas.py

from pydantic import BaseModel
from typing import Optional

# ----------------- Esquemas para Movie -----------------

class MovieBase(BaseModel):
    """
    Esquema base que contiene los campos comunes para evitar repetición.
    """
    nombre: str
    categoria: str
    ano: int
    director: str
    duracion: int
    calificacion: float

class MovieCreate(MovieBase):
    """
    Esquema utilizado para la creación de una película.
    Hereda todos los campos de MovieBase.
    """
    pass

class MovieUpdate(BaseModel):
    """
    Esquema para actualizar una película.
    Todos los campos son opcionales, para permitir actualizaciones parciales.
    """
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    ano: Optional[int] = None
    director: Optional[str] = None
    duracion: Optional[int] = None
    calificacion: Optional[float] = None

class Movie(MovieBase):
    """
    Esquema utilizado para leer/devolver una película desde la API.
    Hereda de MovieBase y añade el 'id' que es generado por la base de datos.
    """
    id: int

    class Config:
        # Habilita el "modo ORM".
        # Le permite a Pydantic leer datos directamente desde los modelos de SQLAlchemy.
        orm_mode = True