import requests

KINOPOISK_API_KEY = "H974FM6-0V3M4CP-HNA5Q7V-ARMKP1B"

def search_films_by_params(params):
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    response = requests.get("https://kinopoiskapiunofficial.tech/api/v2.2/films", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception("Ошибка API Кинопоиска")
    return response.json()

def get_random_series():
    params = {
        "field": "type",
        "value": "TV_SERIES",
        "ratingFrom": 0,
        "ratingTo": 10,
        "yearFrom": 1950,
        "yearTo": 2026,
        "isSerial": True,
        "page": 1
    }
    data = search_films_by_params(params)
    series_list = [
        {
            "id": film["filmId"],
            "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
            "description": film.get("description") or "Описание отсутствует",
            "posterUrl": film.get("posterUrlPreview") or "",
            "year": film.get("year"),
            "genre": film.get("genres")[0]["genre"] if film.get("genres") else None,
            "rating": film.get("rating")
        }
        for film in data["films"]
        if film["type"] == "TV_SERIES"
    ][:5]
    return series_list

def get_random_movie():
    params = {
        "field": "type",
        "value": "FILM",
        "ratingFrom": 0,
        "ratingTo": 10,
        "yearFrom": 1900,
        "yearTo": 2026,
        "isSerial": False,
        "page": 1
    }
    data = search_films_by_params(params)
    movies_list = [
        {
            "id": film["filmId"],
            "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
            "description": film.get("description") or "Описание отсутствует",
            "posterUrl": film.get("posterUrlPreview") or "",
            "year": film.get("year"),
            "genre": film.get("genres")[0]["genre"] if film.get("genres") else None,
            "rating": film.get("rating")
        }
        for film in data["films"]
        if film["type"] == "FILM"
    ][:5]
    return movies_list

def search_films_by_genre_and_year(genre: str, year: int):
    params = {
        "field": "genres.name",
        "value": genre,
        "field": "year",
        "value": str(year),
        "page": 1
    }
    data = search_films_by_params(params)
    return [
        {
            "id": film["filmId"],
            "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
            "description": film.get("description") or "Описание отсутствует",
            "posterUrl": film.get("posterUrlPreview") or "",
            "year": film.get("year"),
            "genre": genre,
            "rating": film.get("rating")
        }
        for film in data["films"]
    ]

def search_films_by_title(title: str):
    params = {
        "field": "name.ru",
        "value": title,
        "page": 1
    }
    data = search_films_by_params(params)
    return [
        {
            "id": film["filmId"],
            "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
            "description": film.get("description") or "Описание отсутствует",
            "posterUrl": film.get("posterUrlPreview") or "",
            "year": film.get("year"),
            "genre": film.get("genres")[0]["genre"] if film.get("genres") else None,
            "rating": film.get("rating")
        }
        for film in data["films"]
    ]

def search_films_by_actor(actor_name: str):
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff?filmId=0&name={actor_name}", headers=headers)
    if response.status_code != 200:
        raise Exception("Ошибка API Кинопоиска")
    staff_data = response.json()
    if not staff_data:
        return []
    # Получаем фильмы по ID актёра
    person_id = staff_data[0]["staffId"]
    film_response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff/{person_id}/films", headers=headers)
    if film_response.status_code != 200:
        raise Exception("Ошибка API Кинопоиска")
    films = film_response.json()
    return [
        {
            "id": film["filmId"],
            "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
            "description": "",
            "posterUrl": "",
            "year": film.get("year"),
            "genre": "",
            "rating": film.get("rating")
        }
        for film in films
    ]