# app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- Esquemas para Reseñas (listos para usarse si hay tiempo) ---
class ReseñaBase(BaseModel):
    calificacion: int
    comentario: Optional[str] = None

class ReseñaCreate(ReseñaBase):
    pass

class Reseña(ReseñaBase):
    id: int
    class Config:
        # ----- CORRECCIÓN AQUÍ -----
        from_attributes = True

# --- Esquemas para Proveedores (Actualizados) ---
class ProveedorBase(BaseModel):
    nombre: str
    tipo_proveedor: str
    descripcion_corta: str
    telefono: str
    direccion: str
    ciudad: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    """
    Esquema para actualizar un proveedor.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    nombre: Optional[str] = None
    tipo_proveedor: Optional[str] = None
    descripcion_corta: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    disponible: Optional[bool] = None

# Esquema para la vista de lista
class ProveedorResumen(BaseModel):
    id: int
    nombre: str
    tipo_proveedor: str
    ciudad: str
    disponible: bool
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    class Config:
        # ----- CORRECCIÓN AQUÍ -----
        from_attributes = True

# Esquema para la vista de detalle
class ProveedorDetalle(ProveedorResumen):
    descripcion_corta: str
    telefono: str
    direccion: str
    reseñas: List[Reseña] = []

    class Config:
        # ----- CORRECCIÓN AQUÍ -----
        from_attributes = True

class ProveedorMapa(BaseModel):
    id: int
    nombre: str
    tipo_proveedor: str
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    descripcion_corta: Optional[str] = None

    class Config:
        from_attributes = True