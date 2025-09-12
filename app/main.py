# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from contextlib import asynccontextmanager
from . import crud, models, schemas
from .database import engine, get_db
from fastapi import FastAPI, BackgroundTasks, HTTPException
from app.ai_service import get_ai_response
from pydantic import BaseModel
from typing import Optional
from .openrouter_client import get_ai_response
from .supabase_client import store_interaction
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from .database import SessionLocal

load_dotenv()

# Esta función 'lifespan' se ejecuta al iniciar la aplicación.
# Aquí le decimos a SQLAlchemy que cree todas las tablas definidas en nuestros modelos.
# Nota: En una aplicación de producción real, se usarían herramientas de migración como Alembic.
#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    async with engine.begin() as conn:
#        await conn.run_sync(models.Base.metadata.create_all)
#    yield

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

# Creamos la instancia de la aplicación FastAPI, pasándole la función lifespan.
app = FastAPI()


# --- Endpoints para Proveedores ---

@app.post("/proveedores", response_model=schemas.ProveedorDetalle, status_code=status.HTTP_201_CREATED, tags=["Proveedores"])
async def create_new_proveedor(proveedor: schemas.ProveedorCreate, db: AsyncSession = Depends(get_db)):
    """Crea un nuevo proveedor. Usado por el formulario de registro."""
    return await crud.create_proveedor(db=db, proveedor=proveedor.dict())

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
    updated_proveedor = await crud.update_proveedor(db, proveedor_id=proveedor_id, proveedor_update=proveedor_update.dict())
    if updated_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return updated_proveedor


class ChatRequest(BaseModel):
    usuario: Optional[str] = None
    preferencias: str
    fechas: Optional[str] = None
    presupuesto: Optional[str] = None
    personas: Optional[int] = 1
    hotel_id: Optional[int] = None  # si el frontend envía hotel elegido

class ChatResponse(BaseModel):
    respuesta: str
    suggestion_followup: Optional[str] = None

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Eres un asesor turístico experto en el Tolima, Colombia. Haz planes claros, prácticos y preguntando lo justo si hace falta."
}

@app.post("/api/ai/chat", response_model=ChatResponse)
async def chat_ai(request: ChatRequest, background_tasks: BackgroundTasks):
    # construimos prompt de usuario integrando los parámetros
    user_content = (
        f"Usuario: {request.usuario or 'Anónimo'}\n"
        f"Preferencias: {request.preferencias}\n"
        f"Fechas: {request.fechas or 'No especificadas'}\n"
        f"Presupuesto: {request.presupuesto or 'No especificado'}\n"
        f"Personas: {request.personas}\n"
    )
    if request.hotel_id:
        user_content += f"HotelID conocido: {request.hotel_id}\n"

    user_message = {"role": "user", "content": user_content}

    try:
        ai_text = await get_ai_response([SYSTEM_PROMPT, user_message])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error AI: {str(e)}")

    # guardamos interacción en background para no bloquear
    background_tasks.add_task(store_interaction, request.usuario, user_content, ai_text, {"hotel_id": request.hotel_id})

    # opcional: generar texto corto de follow up si indica falta de info
    suggestion = None
    if "¿" in ai_text and ("fecha" in ai_text.lower() or "presupuesto" in ai_text.lower()):
        suggestion = "Parece que faltan datos. Pregunta por fechas y presupuesto."

    return {"respuesta": ai_text, "suggestion_followup": suggestion}


@app.get("/hola")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Conexión funcionando 🚀"}