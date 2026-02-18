import requests
import os

# Используем переменную окружения для API-ключа
KINOPOISK_API_KEY = os.getenv("KINOPOISK_API_KEY", "H974FM6-0V3M4CP-HNA5Q7V-ARMKP1B")


def search_films(params):
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    response = requests.get("https://kinopoiskapiunofficial.tech/api/v2.2/films", headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")
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
    data = search_films(params)
    return [
               {
                   "id": f["filmId"],
                   "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
                   "description": f.get("description") or "Описание отсутствует",
                   "posterUrl": f.get("posterUrlPreview") or "",
                   "year": f.get("year"),
                   "genre": f.get("genres")[0]["genre"] if f.get("genres") else None,
                   "rating": f.get("rating")
               }
               for f in data["films"]
               if f.get("type") == "TV_SERIES"
           ][:5]


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
    data = search_films(params)
    return [
               {
                   "id": f["filmId"],
                   "name": f.get("nameRu") or f.get("nameEn") or "Без названия",
                   "description": f.get("description") or "Описание отсутствует",
                   "posterUrl": f.get("posterUrlPreview") or "",
                   "year": f.get("year"),
                   "genre": f.get("genres")[0]["genre"] if f.get("genres") else None,
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
            "genre": f.get("genres")[0]["genre"] if f.get("genres") else None,
            "rating": f.get("rating")
        }
        for f in data["films"]
    ]


def search_by_actor(actor_name: str):
    logger.info(f"Поиск по актёру: '{actor_name}'")
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
    try:
        response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff",
                                headers=headers,
                                params={"name": actor_name})
        logger.info(f"Ответ от API персон: статус {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Ошибка API персон: {response.status_code}, текст: {response.text}")
            raise Exception(f"Actor API error {response.status_code}: {response.text}")

        staff_data = response.json()
        if not staff_data:
            logger.warning("Персон не найден")
            return []

        person = staff_data[0]
        person_id = person.get("staffId")
        if not person_id:
            logger.error("staffId отсутствует в ответе")
            return []

        film_response = requests.get(f"https://kinopoiskapiunofficial.tech/api/v1/staff/{person_id}/films",
                                     headers=headers)
        logger.info(f"Ответ от API фильмов: статус {film_response.status_code}")

        if film_response.status_code != 200:
            logger.error(f"Ошибка API фильмов: {film_response.status_code}, текст: {film_response.text}")
            raise Exception(f"Film API error {film_response.status_code}: {film_response.text}")

        films = film_response.json()
        result = [
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
        logger.info(f"Найдено {len(result)} фильмов по актёру")
        return result
    except Exception as e:
        logger.error(f"Ошибка в search_by_actor: {e}")
        raise