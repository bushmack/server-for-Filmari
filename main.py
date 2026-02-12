from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from models import Film, UserCollection
from database import init_db, add_film_to_collection, get_user_collections
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from kinopoisk_api import (
    get_random_series,
    get_random_movie,
    search_by_genre_and_year,
    search_by_title,
    search_by_actor
)

app = FastAPI(title="Full Film API Server")
init_db()

@app.get("/")
async def root():
    logger.info("Запрос к корню сервера")
    return {"message": "Film API Server", "status": "running"}

@app.get("/api/random-series", response_model=List[Film])
async def api_get_random_series():
    logger.info("Получен запрос на получение случайных сериалов")
    try:
        result = get_random_series()
        logger.info(f"Отправлено {len(result)} сериалов")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_get_random_series: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/random-movie", response_model=List[Film])
async def api_get_random_movie():
    logger.info("Получен запрос на получение случайных фильмов")
    try:
        result = get_random_movie()
        logger.info(f"Отправлено {len(result)} фильмов")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_get_random_movie: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-genre-year", response_model=List[Film])
async def api_search_by_genre_year(genre: str, year: int):
    logger.info(f"Получен запрос на поиск по жанру '{genre}' и году '{year}'")
    try:
        result = search_by_genre_and_year(genre, year)
        logger.info(f"Отправлено {len(result)} фильмов по жанру и году")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_search_by_genre_year: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-title", response_model=List[Film])
async def api_search_by_title(title: str = Query(..., min_length=1)):
    logger.info(f"Получен запрос на поиск по названию: '{title}'")
    try:
        result = search_by_title(title)
        logger.info(f"Отправлено {len(result)} фильмов по названию")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_search_by_title: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-actor", response_model=List[Film])
async def api_search_by_actor(actor: str = Query(..., min_length=1)):
    logger.info(f"Получен запрос на поиск по актёру: '{actor}'")
    try:
        result = search_by_actor(actor)
        logger.info(f"Отправлено {len(result)} фильмов по актёру")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_search_by_actor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add-to-collection")
async def api_add_to_collection(user_id: str, film_id: int):
    logger.info(f"Получен запрос на добавление фильма {film_id} пользователю {user_id}")
    try:
        add_film_to_collection(user_id, film_id)
        logger.info(f"Фильм {film_id} успешно добавлен пользователю {user_id}")
        return {"message": "Фильм добавлен в подборку"}
    except Exception as e:
        logger.error(f"Ошибка в api_add_to_collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-collections/{user_id}", response_model=List[int])
async def api_get_user_collections_endpoint(user_id: str):
    logger.info(f"Получен запрос на получение подборки пользователя {user_id}")
    try:
        result = get_user_collections(user_id)
        logger.info(f"Отправлено {len(result)} фильмов из подборки пользователя {user_id}")
        return result
    except Exception as e:
        logger.error(f"Ошибка в api_get_user_collections_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Исправленное условие
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)