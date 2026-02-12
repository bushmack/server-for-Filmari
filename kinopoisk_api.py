import requests
import os

# Используем переменную окружения для API-ключа
KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY")
if not KINOPOISK_API_KEY:
    raise ValueError("Не установлен API-ключ KINOPOISK_API_KEY")

def search_films(params):
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    response = requests.get("https://kinopoiskapiunofficial.tech/api/v2.2/films", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
    return response.json()

def get_random_series():
    params = [
        ("field", "type"),
        ("value", "TV_SERIES"),
        ("ratingFrom", 0),
        ("ratingTo", 10),
        ("yearFrom", 1950),
        ("yearTo", 2026),
        ("isSerial", True),
        ("page", 1)
    ]
    data = search_films(params)
    return [
        {
            "id": f["filmId"],
            "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
            "description": f.get("description") or "Описание отсутствует",
            "posterUrl": f.get("posterUrlPreview") or "",
            "year": f.get("year"),
            "genre": f.get("genres")[0]["genre"] if f.get("genres") and len(f.get("genres")) > 0 else None,
            "rating": f.get("rating")
        }
        for f in data["films"]
        if f.get("type") == "TV_SERIES"
    ][:5]

def get_random_movie():
    params = [
        ("field", "type"),
        ("value", "FILM"),
        ("ratingFrom", 0),
        ("ratingTo", 10),
        ("yearFrom", 1900),
        ("yearTo", 2026),
        ("isSerial", False),
        ("page", 1)
    ]
    data = search_films(params)
    return [
        {
            "id": f["filmId"],
            "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
            "description": f.get("description") or "Описание отсутствует",
            "posterUrl": f.get("posterUrlPreview") or "",
            "year": f.get("year"),
            "genre": f.get("genres")[0]["genre"] if f.get("genres") and len(f.get("genres")) > 0 else None,
            "rating": f.get("rating")
        }
        for f in data["films"]
        if f.get("type") == "FILM"
    ][:5]

def search_by_genre_and_year(genre: str, year: int):
    params = [
        ("field", "genres.name"),
        ("value", genre),
        ("field", "year"),
        ("value", str(year)),
        ("page", 1)
    ]
    data = search_films(params)
    return [
        {
            "id": f["filmId"],
            "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
            "description": f.get("description") or "Описание отсутствует",
            "posterUrl": f.get("posterUrlPreview") or "",
            "year": f.get("year"),
            "genre": genre,
            "rating": f.get("rating")
        }
        for f in data["films"]
    ]

def search_by_title(title: str):
    params = {
        "field": "name.ru",
        "value": title,
        "page": 1
    }
    data = search_films(params)
    return [
        {
            "id": f["filmId"],
            "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
            "description": f.get("description") or "Описание отсутствует",
            "posterUrl": f.get("posterUrlPreview") or "",
            "year": f.get("year"),
            "genre": f.get("genres")[0]["genre"] if f.get("genres") and len(f.get("genres")) > 0 else None,
            "rating": f.get("rating")
        }
        for f in data["films"]
    ]

def search_by_actor(actor_name: str):
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff?filmId=0&name={actor_name}", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Actor API error {response.status_code}: {response.text}")
    
    staff_data = response.json()
    if not staff_data:
        return []

    person = staff_data[0]
    person_id = person.get("staffId")
    if not person_id:
        return []

    film_response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff/{person_id}/films", headers=headers)
    if film_response.status_code != 200:
        raise Exception(f"Film API error {film_response.status_code}: {film_response.text}")

    films = film_response.json()
    return [
        {
            "id": f["filmId"],
            "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
            "description": f.get("description") or "Описание отсутствует",
            "posterUrl": f.get("posterUrlPreview") or "",
            "year": f.get("year"),
            "genre": f.get("genres")[0]["genre"] if f.get("genres") and len(f.get("genres")) > 0 else None,
            "rating": f.get("rating")
        }
        for f in films
    ]