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


@app.post("/peliculas", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED, tags=["Películas"])
async def create_new_movie(movie: schemas.MovieCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva película en la base de datos.
    """
    return await crud.create_movie(db=db, movie=movie)


@app.get("/peliculas", response_model=List[schemas.Movie], tags=["Películas"])
async def read_movies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Obtiene una lista de todas las películas con paginación.
    """
    movies = await crud.get_movies(db, skip=skip, limit=limit)
    return movies


@app.get("/peliculas/{movie_id}", response_model=schemas.Movie, tags=["Películas"])
async def read_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene los detalles de una película por su ID.
    """
    db_movie = await crud.get_movie(db, movie_id=movie_id)
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return db_movie


@app.put("/peliculas/{movie_id}", response_model=schemas.Movie, tags=["Películas"])
async def update_existing_movie(movie_id: int, movie_update: schemas.MovieUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza una película existente por su ID.
    """
    updated_movie = await crud.update_movie(db, movie_id=movie_id, movie_update=movie_update)
    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return updated_movie


@app.delete("/peliculas/{movie_id}", response_model=schemas.Movie, tags=["Películas"])
async def delete_existing_movie(movie_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una película existente por su ID.
    """
    deleted_movie = await crud.delete_movie(db, movie_id=movie_id)
    if deleted_movie is None:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return deleted_movie

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