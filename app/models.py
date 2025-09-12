# app/models.py
from sqlalchemy import (Column, Integer, String, Boolean, Text, Float, 
                        ForeignKey, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

from .database import Base

class Proveedor(Base):
    """
    Modelo Definitivo de Proveedor.
    Soporta el MVP, la geolocalización y está listo para las reseñas.
    """
    __tablename__ = "proveedores"

    # --- Campos del MVP y Generales ---
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    tipo_proveedor = Column(String(50), index=True, nullable=False) # Hotel, Transporte, Guía, etc.
    descripcion_corta = Column(String(255))
    telefono = Column(String(20), unique=True)
    
    # --- Prioridad #1: Disponibilidad con Checkbox ---
    disponible = Column(Boolean, default=True)

    # --- Prioridad #2: Geolocalización para el Mapa ---
    direccion = Column(String(255))
    ciudad = Column(String(100), index=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)

    # --- Bonus (si hay tiempo): Preparado para Reseñas ---
    # Esta relación prepara el terreno para las reseñas sin obligarnos a implementarlas ya.
    reseñas = relationship("Reseña", back_populates="proveedor", cascade="all, delete-orphan")


class Reseña(Base):
    """
    Modelo para Reseñas. Lo dejamos aquí listo para cuando haya tiempo.
    """
    __tablename__ = "reseñas"

    id = Column(Integer, primary_key=True, index=True)
    calificacion = Column(Integer, index=True) # Estrellas (1 a 5)
    comentario = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    proveedor = relationship("Proveedor", back_populates="reseñas")