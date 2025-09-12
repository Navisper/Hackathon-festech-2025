# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from sqlalchemy.orm import selectinload
from . import models, schemas

# --- Funciones CRUD para Proveedores ---

async def get_proveedor(db: AsyncSession, proveedor_id: int):
    """Busca un proveedor por su ID."""
    query = (
        select(models.Proveedor)
        .where(models.Proveedor.id == proveedor_id)
        .options(selectinload(models.Proveedor.reseñas))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_proveedores(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Obtiene una lista de todos los proveedores."""
    result = await db.execute(select(models.Proveedor).offset(skip).limit(limit))
    return result.scalars().all()

async def create_proveedor(db: AsyncSession, proveedor: schemas.ProveedorCreate):
    """Crea un nuevo proveedor en la base de datos."""
    db_proveedor = models.Proveedor(**proveedor.dict())
    db.add(db_proveedor)
    await db.commit()
    await db.refresh(db_proveedor)
    return await get_proveedor(db, db_proveedor.id)

async def update_proveedor(db: AsyncSession, proveedor_id: int, proveedor_update: schemas.ProveedorUpdate):
    """
    Actualiza un proveedor existente.
    Perfecto para el checkbox de disponibilidad.
    """
    db_proveedor = await get_proveedor(db, proveedor_id)
    if not db_proveedor:
        return None
    
    update_data = proveedor_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_proveedor, key, value)
        
    await db.commit()
    await db.refresh(db_proveedor)
    return await get_proveedor(db, db_proveedor.id)

async def delete_proveedor(db: AsyncSession, proveedor_id: int):
    """Elimina un proveedor de la base de datos."""
    db_proveedor = await get_proveedor(db, proveedor_id)
    if not db_proveedor:
        return None
    
    await db.delete(db_proveedor)
    await db.commit()
    return db_proveedor

# --- (BONUS) Funciones CRUD para Reseñas (si hay tiempo) ---

async def create_reseña_para_proveedor(db: AsyncSession, reseña: schemas.ReseñaCreate, proveedor_id: int):
    """Crea una reseña y la asocia con un proveedor."""
    db_reseña = models.Reseña(**reseña.dict(), proveedor_id=proveedor_id)
    db.add(db_reseña)
    await db.commit()
    await db.refresh(db_reseña)
    return db_reseña

async def get_reseñas_de_proveedor(db: AsyncSession, proveedor_id: int, skip: int = 0, limit: int = 100):
    """Obtiene todas las reseñas de un proveedor específico."""
    result = await db.execute(
        select(models.Reseña)
        .filter(models.Reseña.proveedor_id == proveedor_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()