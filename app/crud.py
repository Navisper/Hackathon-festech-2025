# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import models, schemas

async def get_movie(db: AsyncSession, movie_id: int):
    """
    Busca una película por su ID.
    """
    result = await db.execute(select(models.Movie).filter(models.Movie.id == movie_id))
    return result.scalar_one_or_none()

async def get_movies(db: AsyncSession, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de películas con paginación.
    """
    result = await db.execute(select(models.Movie).offset(skip).limit(limit))
    return result.scalars().all()

async def create_movie(db: AsyncSession, movie: schemas.MovieCreate):
    """
    Crea una nueva película en la base de datos.
    """
    # Convierte el schema de Pydantic a un modelo de SQLAlchemy
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    await db.commit()
    await db.refresh(db_movie) # Refresca el objeto para obtener el ID de la BD
    return db_movie

async def update_movie(db: AsyncSession, movie_id: int, movie_update: schemas.MovieUpdate):
    """
    Actualiza una película existente.
    """
    db_movie = await get_movie(db, movie_id)
    if not db_movie:
        return None
    
    # Obtiene los datos del schema de actualización como un diccionario
    # exclude_unset=True asegura que solo actualicemos los campos que el usuario envió
    update_data = movie_update.dict(exclude_unset=True)
    
    # Itera sobre los datos y actualiza los atributos del objeto SQLAlchemy
    for key, value in update_data.items():
        setattr(db_movie, key, value)
        
    await db.commit()
    await db.refresh(db_movie)
    return db_movie

async def delete_movie(db: AsyncSession, movie_id: int):
    """
    Elimina una película de la base de datos.
    """
    db_movie = await get_movie(db, movie_id)
    if not db_movie:
        return None
    
    await db.delete(db_movie)
    await db.commit()
    return db_movie