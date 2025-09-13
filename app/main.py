# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from contextlib import asynccontextmanager
from pydantic import BaseModel
from .schemas import ProveedorMapa
# Tus importaciones existentes
from . import crud, models, schemas
from .database import engine, get_db

# Nueva importación para el servicio de IA
from .ai_service import get_ai_response

#Importacion CORS
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Esto crea las tablas 'proveedores' y 'reseñas' al iniciar
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan, title="Tolima Conecta API")

# Middleware de CORS para desarrollo local
origins = ["*"] # Permite todas las conexiones

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints para Proveedores (Sin cambios) ---

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

@app.delete("/proveedores/{proveedor_id}", response_model=schemas.ProveedorDetalle, tags=["Proveedores"])
async def delete_existing_proveedor(proveedor_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina un proveedor y todas sus reseñas asociadas (en cascada).
    """
    deleted_proveedor = await crud.delete_proveedor(db, proveedor_id=proveedor_id)
    if deleted_proveedor is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return deleted_proveedor

@app.get("/api/servicios", response_model=List[ProveedorMapa], tags=["Mapa"])
async def get_proveedores_mapa(tipo: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """
    Devuelve proveedores con coordenadas (para el mapa).
    Se puede filtrar por tipo (hotel, restaurante, transporte, atracción, etc.).
    """
    proveedores = await crud.get_proveedores_mapa(db, tipo)
    return proveedores

# --- (BONUS) Endpoints para Reseñas (Sin cambios) ---

@app.post("/proveedores/{proveedor_id}/reseñas", response_model=schemas.Reseña, status_code=status.HTTP_201_CREATED, tags=["Reseñas"])
async def create_review_for_proveedor(proveedor_id: int, reseña: schemas.ReseñaCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva reseña para un proveedor específico."""
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

@app.delete("/reseñas/{reseña_id}", response_model=schemas.Reseña, tags=["Reseñas"])
async def delete_existing_reseña(reseña_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una reseña específica por su ID.
    """
    deleted_reseña = await crud.delete_reseña(db, reseña_id=reseña_id)
    if deleted_reseña is None:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return deleted_reseña


# ----- INICIO DE LA INTEGRACIÓN DE IA -----

# 1. Definimos los modelos de Pydantic para la petición y respuesta del chat
class ChatRequest(BaseModel):
    usuario: Optional[str] = "Anónimo"
    preferencias: str
    fechas: Optional[str] = None
    presupuesto: Optional[str] = None
    personas: Optional[int] = 1

class ChatResponse(BaseModel):
    respuesta: str

# 2. Definimos el prompt del sistema para la IA
SYSTEM_PROMPT = {
    "role": "system",
    "content": "Eres un asesor turístico experto en el Tolima, Colombia. Tu objetivo es ayudar al usuario a planificar un viaje increíble. Usa la información de los proveedores disponibles para dar recomendaciones concretas. Sé amable y conversacional, claro y conciso. ayudate de los proveedores de la base de datos para dar info si hay disponible"
}

# 3. Creamos el endpoint principal del chat
@app.post("/api/ai/chat", response_model=ChatResponse, tags=["IA Turística"])
async def chat_ai(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    
    # Obtenemos la información de todos los proveedores disponibles desde nuestra base de datos
    proveedores_disponibles = await crud.get_proveedores(db, limit=100) # Usamos un límite razonable
    
    # Creamos un contexto con la información de los proveedores para la IA
    contexto_proveedores = "Proveedores Disponibles en Tolima:\n"
    for p in proveedores_disponibles:
        if p.disponible: # Solo incluimos los que están marcados como disponibles
            contexto_proveedores += f"- ID: {p.id}, Nombre: {p.nombre}, Tipo: {p.tipo_proveedor}, Ciudad: {p.ciudad}, Descripción: {p.descripcion_corta}\n"

    # Construimos el prompt final para el usuario
    user_content = (
        f"Aquí tienes información sobre los proveedores actuales:\n{contexto_proveedores}\n"
        f"--- \n"
        f"Ahora, por favor, ayúdame con mi viaje. Mis preferencias son:\n"
        f"Preferencias: {request.preferencias}\n"
        f"Fechas: {request.fechas or 'No especificadas'}\n"
        f"Presupuesto: {request.presupuesto or 'No especificado'}\n"
        f"Número de personas: {request.personas}\n"
    )

    user_message = {"role": "user", "content": user_content}

    try:
        # Llamamos al servicio de IA con el contexto y la petición del usuario
        ai_text = await get_ai_response([SYSTEM_PROMPT, user_message])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al contactar el servicio de IA: {str(e)}")

    return ChatResponse(respuesta=ai_text)

# ----- FIN DE LA INTEGRACIÓN DE IA -----