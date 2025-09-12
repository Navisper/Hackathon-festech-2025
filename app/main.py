# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from contextlib import asynccontextmanager

from . import crud, models, schemas
from .database import engine, get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Esto crea las tablas 'proveedores' y 'reseñas' al iniciar
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan, title="Tolima Conecta API")


# --- Endpoints para Proveedores (Prioridad #1 y #2) ---

@app.post("/proveedores", response_model=schemas.ProveedorDetalle, status_code=status.HTTP_201_CREATED, tags=["Proveedores"])
async def create_new_proveedor(proveedor: schemas.ProveedorCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo proveedor. Usado por el formulario de registro."""
    return await crud.create_proveedor(db=db, proveedor=proveedor)

@app.get("/proveedores", response_model=List[schemas.ProveedorResumen], tags=["Proveedores"])
async def read_proveedores(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Obtiene una lista de todos los proveedores para el mapa y la lista principal."""
    proveedores = await crud.get_proveedores(db, skip=skip, limit=limit)
    return proveedores

@app.get("/proveedores/{proveedor_id}", response_model=schemas.ProveedorDetalle, tags=["Proveedores"])
async def read_proveedor_details(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene la vista detallada de un solo proveedor."""
    db_proveedor = await crud.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return db_proveedor

@app.put("/proveedores/{proveedor_id}", response_model=schemas.ProveedorDetalle, tags=["Proveedores"])
async def update_existing_proveedor(proveedor_id: int, proveedor_update: schemas.ProveedorUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza un proveedor. Principalmente para el **checkbox de disponibilidad**.
    El frontend solo necesita enviar `{"disponible": false}`.
    """
    updated_proveedor = await crud.update_proveedor(db, proveedor_id=proveedor_id, proveedor_update=proveedor_update)
    if updated_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return updated_proveedor


# --- (BONUS) Endpoints para Reseñas (si hay tiempo) ---

@app.post("/proveedores/{proveedor_id}/reseñas", response_model=schemas.Reseña, status_code=status.HTTP_201_CREATED, tags=["Reseñas"])
async def create_review_for_proveedor(proveedor_id: int, reseña: schemas.ReseñaCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva reseña para un proveedor específico."""
    # Primero, verificamos que el proveedor exista
    db_proveedor = await crud.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado, no se puede crear la reseña.")
    return await crud.create_reseña_para_proveedor(db=db, reseña=reseña, proveedor_id=proveedor_id)

@app.get("/proveedores/{proveedor_id}/reseñas", response_model=List[schemas.Reseña], tags=["Reseñas"])
async def read_reviews_for_proveedor(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene todas las reseñas de un proveedor específico."""
    db_proveedor = await crud.get_proveedor(db, proveedor_id=proveedor_id)
    if db_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado.")
    return await crud.get_reseñas_de_proveedor(db=db, proveedor_id=proveedor_id)