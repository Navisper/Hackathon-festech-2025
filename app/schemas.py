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
        orm_mode = True

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
        orm_mode = True

# Esquema para la vista de detalle
class ProveedorDetalle(ProveedorResumen):
    descripcion_corta: str
    telefono: str
    direccion: str
    # Si implementan las reseñas, este campo ya estará listo para usarse
    reseñas: List[Reseña] = []

    class Config:
        orm_mode = True