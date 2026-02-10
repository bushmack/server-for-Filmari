import requests
from typing import List, Dict, Any

KINOPOISK_API_KEY = "H974FM6-0V3M4CP-HNA5Q7V-ARMKP1B"
BASE_URL = "https://kinopoiskapiunofficial.tech/api/v2.2/films"


def get_random_series(limit: int = 5) -> List[Dict[str, Any]]:
    headers = {"X-API-KEY": KINOPOISK_API_KEY}
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
    response = requests.get(BASE_URL, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Ошибка API Кинопоиска: {response.status_code}")

    data = response.json()
    series_list = [
                      {
                          "id": film["filmId"],
                          "name": film.get("nameRu") or film.get("nameEn") or "Без названия",
                          "description": film.get("description") or "Описание отсутствует",
                          "posterUrl": film.get("posterUrlPreview") or ""
                      }
                      for film in data["films"]
                      if film["type"] == "TV_SERIES"
                  ][:limit]

    return series_list