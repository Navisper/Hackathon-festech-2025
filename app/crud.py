# crud.py
from sqlalchemy import select
from . import models, schemas
from sqlalchemy.orm import Session

def get_proveedores(db: Session, skip: int = 0, limit: int = 100):
    result = db.execute(select(models.Proveedor).offset(skip).limit(limit))
    return result.scalars().all()

def get_proveedor(db: Session, proveedor_id: int):
    result = db.execute(
        select(models.Proveedor).where(models.Proveedor.id == proveedor_id)
    )
    return result.scalars().first()

def create_proveedor(db: Session, proveedor: schemas.ProveedorCreate):
    db_proveedor = models.Proveedor(**proveedor.dict())
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

def update_proveedor(db: Session, proveedor_id: int, proveedor_update: schemas.ProveedorUpdate):
    proveedor_db = get_proveedor(db, proveedor_id)
    if not proveedor_db:
        return None
    for key, value in proveedor_update.dict().items():
        setattr(proveedor_db, key, value)
    db.add(proveedor_db)
    db.commit()
    db.refresh(proveedor_db)
    return proveedor_db
