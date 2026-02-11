import uuid
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from models import Film
from database import (
    init_db,
    add_film_to_collection,
    get_user_collections,
    create_pair_session,
    save_genres_for_user_in_session,
    get_genres_for_users_in_session,
    save_vote_in_session,
    get_votes_in_session,
    get_users_in_session,
    add_shown_film_to_session,
    get_shown_films_in_session
)
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

# --- Мои подборки ---
@app.get("/api/my-collections/{user_id}", response_model=List[Film])
async def api_get_my_collections(user_id: str):
    try:
        film_ids = get_user_collections(user_id)
        if not film_ids:
            return []
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Случайный сериал ---
@app.get("/api/random-series", response_model=List[Film])
async def api_get_random_series():
    try:
        return get_random_series()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Случайный фильм ---
@app.get("/api/random-movie", response_model=List[Film])
async def api_get_random_movie():
    try:
        return get_random_movie()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Поиск по жанру и году ---
@app.get("/api/search-by-genre-year", response_model=List[Film])
async def api_search_by_genre_year(genre: str, year: int):
    try:
        return search_by_genre_and_year(genre, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Поиск по названию ---
@app.get("/api/search-by-title", response_model=List[Film])
async def api_search_by_title(title: str = Query(..., min_length=1)):
    try:
        return search_by_title(title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Поиск по актёру ---
@app.get("/api/search-by-actor", response_model=List[Film])
async def api_search_by_actor(actor: str = Query(..., min_length=1)):
    try:
        return search_by_actor(actor)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Добавить в подборку ---
@app.post("/api/add-to-collection")
async def api_add_to_collection(user_id: str, film_id: int):
    try:
        add_film_to_collection(user_id, film_id)
        return {"message": "Фильм добавлен в подборку"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Парный выбор ---

@app.post("/api/pair-session/create")
async def create_pair_session_endpoint(user_a: str = Query(...), user_b: str = Query(...)):
    session_id = str(uuid.uuid4())
    create_pair_session(session_id, user_a, user_b)
    return {"session_id": session_id}

@app.post("/api/pair-session/{session_id}/set-genres")
async def set_genres_in_session(session_id: str, user_id: str = Query(...), genres: List[str] = Query(...)):
    save_genres_for_user_in_session(session_id, user_id, genres)
    return {"message": "Genres saved"}

@app.get("/api/pair-session/{session_id}/next-film")
async def get_next_film_for_session(session_id: str):
    shown = set(get_shown_films_in_session(session_id))

    genres_map = get_genres_for_users_in_session(session_id)
    if not genres_map:
        raise HTTPException(status_code=400, detail="No genres selected by users yet")

    user_a, user_b = get_users_in_session(session_id)
    if not user_a or not user_b:
        raise HTTPException(status_code=400, detail="Session has no users")

    genres_a = set(genres_map.get(user_a, []))
    genres_b = set(genres_map.get(user_b, []))
    common_genres = genres_a & genres_b

    films = []
    if common_genres:
        for genre in common_genres:
            films.extend(search_by_genre_and_year(genre, 2026))
    else:
        films = get_random_movie()

    # Фильтруем уже показанные фильмы
    filtered_films = [f for f in films if f["id"] not in shown]

    if not filtered_films:
        raise HTTPException(status_code=404, detail="No more films available for this session")

    next_film = filtered_films[0]
    add_shown_film_to_session(session_id, next_film["id"])
    return next_film

@app.post("/api/pair-session/{session_id}/vote")
async def vote_in_session(session_id: str, user_id: str = Query(...), film_id: int = Query(...), like: bool = Query(...)):
    save_vote_in_session(session_id, user_id, film_id, like)

    votes = get_votes_in_session(session_id)
    user_a, user_b = get_users_in_session(session_id)

    votes_a = votes.get(user_a, {})
    votes_b = votes.get(user_b, {})

    liked_by_both = set(
        fid for fid, v in votes_a.items() if v and votes_b.get(fid) == True
    )

    if liked_by_both:
        matched_film_id = list(liked_by_both)[0]
        return {"match": True, "film": {"id": matched_film_id}}

    return {"match": False}

@app.get("/api/pair-session/{session_id}/result")
async def get_match_result(session_id: str):
    votes = get_votes_in_session(session_id)
    user_a, user_b = get_users_in_session(session_id)

    votes_a = votes.get(user_a, {})
    votes_b = votes.get(user_b, {})

    liked_by_both = set(
        fid for fid, v in votes_a.items() if v and votes_b.get(fid) == True
    )

    return {"matches": list(liked_by_both)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)