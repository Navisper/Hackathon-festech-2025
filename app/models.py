# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB # Importamos el tipo JSONB

from .database import Base

class Proveedor(Base):
    """
    Modelo SQLAlchemy mejorado para proveedores turísticos.
    Combina campos estructurados con campos flexibles (JSONB) para máxima adaptabilidad.
    """
    __tablename__ = "proveedores" 

    # --- ATRIBUTOS ESTRUCTURADOS (El Núcleo) ---
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True, nullable=False)
    tipo_proveedor = Column(String(50), index=True) # "Hotel", "Guía", "Restaurante", "Experiencia"
    
    # Descripciones para diferentes vistas
    descripcion_corta = Column(String(255)) # Para la tarjeta de resumen en la landing
    descripcion_larga = Column(Text) # Para la vista de detalle
    
    # Información de Contacto y Ubicación
    direccion = Column(String(255))
    ciudad = Column(String(100), index=True)
    telefono = Column(String(20), unique=True)
    email = Column(String(100), unique=True)
    sitio_web = Column(String(255), nullable=True)

    # Atributos Generalizados Clave
    capacidad_maxima = Column(Integer, nullable=True) # Sirve para 'Nº de habitaciones', 'Cupos del tour', 'Mesas del restaurante'
    rango_precios = Column(String(50), nullable=True) # "Económico", "$50-$100", "Premium"
    
    verificado = Column(Boolean, default=False)

    # --- ATRIBUTOS FLEXIBLES (La Magia) ---
    tags = Column(JSONB, nullable=True) # Una lista de etiquetas: ["Sostenible", "Aventura", "Familias", "Pet-Friendly"]
    atributos_adicionales = Column(JSONB, nullable=True) # Un diccionario para detalles específicos: {"estrellas": 5, "wifi_gratis": True, "idiomas": ["Español", "Inglés"]}