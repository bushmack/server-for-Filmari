import httpx
import asyncio
import random
from typing import List, Optional
from models import Film


class KinopoiskAPI:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.kinopoisk.dev/v1.4"
        self.headers = {
            "X-API-KEY": api_token,
            "Content-Type": "application/json"
        }

    async def get_random_movies(self, count: int = 5) -> List[Film]:
        """
        Получение случайных фильмов через API Кинопоиска
        """
        all_movies = []

        # Получаем несколько страниц со случайными фильмами
        for page in range(1, 4):  # Получаем 3 страницы для разнообразия
            try:
                async with httpx.AsyncClient() as client:
                    # Параметры запроса для получения разных фильмов
                    params = {
                        "page": page,
                        "limit": 50,  # Максимальное количество на странице
                        "selectFields": ["id", "name", "alternativeName", "year",
                                         "description", "rating", "poster",
                                         "countries", "genres", "movieLength", "ageRating"],
                        "notNullFields": ["name", "description", "poster.url"]
                    }

                    response = await client.get(
                        f"{self.base_url}/movie",
                        headers=self.headers,
                        params=params,
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        data = response.json()
                        movies = data.get("docs", [])
                        all_movies.extend(movies)

            except Exception as e:
                print(f"Ошибка при получении страницы {page}: {e}")
                continue

        # Перемешиваем и выбираем случайные фильмы
        random.shuffle(all_movies)
        selected_movies = all_movies[:count]

        # Преобразуем в модели Pydantic
        return [Film(**movie) for movie in selected_movies]

    async def get_random_movies_by_year(self, count: int = 5, year: Optional[int] = None) -> List[Film]:
        """
        Получение случайных фильмов определенного года
        """
        movies = []

        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "page": random.randint(1, 5),  # Случайная страница
                    "limit": 50,
                    "selectFields": ["id", "name", "alternativeName", "year",
                                     "description", "rating", "poster",
                                     "countries", "genres", "movieLength", "ageRating"],
                    "notNullFields": ["name", "description", "poster.url"]
                }

                if year:
                    params["year"] = year

                response = await client.get(
                    f"{self.base_url}/movie",
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()
                    all_movies = data.get("docs", [])
                    random.shuffle(all_movies)
                    movies = all_movies[:count]

        except Exception as e:
            print(f"Ошибка при получении фильмов: {e}")

        return [Film(**movie) for movie in movies]