from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from models import Film, UserCollection
from database import init_db, add_film_to_collection, get_user_collections
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
    return {"message": "Film API Server", "status": "running"}

@app.get("/api/random-series", response_model=List[Film])
async def api_get_random_series():
    try:
        return get_random_series()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/random-movie", response_model=List[Film])
async def api_get_random_movie():
    try:
        return get_random_movie()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-genre-year", response_model=List[Film])
async def api_search_by_genre_year(genre: str, year: int):
    try:
        return search_by_genre_and_year(genre, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-title", response_model=List[Film])
async def api_search_by_title(title: str = Query(..., min_length=1)):
    try:
        return search_by_title(title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-actor", response_model=List[Film])
async def api_search_by_actor(actor: str = Query(..., min_length=1)):
    try:
        return search_by_actor(actor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add-to-collection")
async def api_add_to_collection(user_id: str, film_id: int):
    try:
        add_film_to_collection(user_id, film_id)
        return {"message": "Фильм добавлен в подборку"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-collections/{user_id}", response_model=List[int])
async def api_get_user_collections_endpoint(user_id: str):
    try:
        return get_user_collections(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)