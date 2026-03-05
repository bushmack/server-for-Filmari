from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from typing import List, Optional
import httpx
import random
import asyncio
from collections import OrderedDict
import time

load_dotenv()

app = FastAPI(title="Kinopoisk API для WPF приложения")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TTLCache:
    def __init__(self, ttl_seconds=300, max_size=200):
        self.cache = OrderedDict()
        self.ttl = ttl_seconds
        self.max_size = max_size

    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        self.cache[key] = (value, time.time())


class KinopoiskAPI:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.kinopoisk.dev/v1.4"
        self.headers = {"X-API-KEY": api_token}
        self.my_collections = []

        # Кэш только для поиска и фильмов по ID
        self.movies_cache = TTLCache(ttl_seconds=300)
        self.search_cache = TTLCache(ttl_seconds=300)

        # ДЛЯ СЛУЧАЙНЫХ ФИЛЬМОВ КЭША НЕТ!

    async def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Базовый метод для запросов к API"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                url = f"{self.base_url}{endpoint}"
                print(f"Запрос к: {url}")

                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"Ошибка API: {response.status_code}")
                    return {"docs": []}
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return {"docs": []}

    def _convert_to_wpf_format(self, movie: dict) -> dict:
        """Конвертирует фильм в формат WPF со всеми жанрами"""
        # ВСЕ жанры
        genres = []
        if movie.get("genres"):
            genres = [g.get("name", "") for g in movie["genres"] if g.get("name")]

        # Первый жанр для поля Genre (для обратной совместимости)
        genre = genres[0] if genres else ""

        # Рейтинг
        rating = None
        if movie.get("rating"):
            rating = movie["rating"].get("kp") or movie["rating"].get("imdb")

        # Постер
        poster_url = ""
        if movie.get("poster"):
            poster_url = movie["poster"].get("url") or movie["poster"].get("previewUrl", "")

        # Актеры
        actors = []
        if movie.get("persons"):
            for p in movie["persons"]:
                if p.get("profession") == "актеры" and p.get("name"):
                    actors.append(p.get("name", ""))

        # Режиссеры
        directors = []
        if movie.get("persons"):
            for p in movie["persons"]:
                if p.get("profession") == "режиссеры" and p.get("name"):
                    directors.append(p.get("name", ""))

        # Страны
        countries = []
        if movie.get("countries"):
            countries = [c.get("name", "") for c in movie["countries"] if c.get("name")]

        # Первая страна для поля Country
        country = countries[0] if countries else ""

        # Длительность
        movie_length = movie.get("movieLength")

        # Информация о сезонах
        seasons_info = None
        seasons_text = ""
        if movie.get("seasonsInfo"):
            total_episodes = 0
            seasons = []
            for season in movie.get("seasonsInfo", []):
                episodes = season.get("episodesCount", 0)
                total_episodes += episodes
                seasons.append({
                    "number": season.get("number", 0),
                    "episodes": episodes
                })
            seasons_info = {
                "seasons": seasons,
                "total_seasons": len(seasons),
                "total_episodes": total_episodes
            }
            seasons_text = f"{len(seasons)} сезонов, {total_episodes} серий"

        return {
            "Id": movie.get("id", 0),
            "Name": movie.get("name") or movie.get("alternativeName", "Без названия"),
            "Description": movie.get("description") or movie.get("shortDescription") or "Описание отсутствует",
            "PosterUrl": poster_url,
            "Year": movie.get("year"),
            "Genre": genre,  # Первый жанр (для обратной совместимости)
            "AllGenres": genres,  # ВСЕ жанры
            "GenresString": ", ".join(genres),  # Строка со всеми жанрами
            "Rating": round(rating, 1) if rating else None,
            "Type": movie.get("type", "movie"),
            "Actors": actors[:10],
            "Directors": directors,
            "Countries": countries,
            "Country": country,
            "MovieLength": movie_length,
            "AgeRating": movie.get("ageRating"),
            "SeasonsInfo": seasons_info,
            "SeasonsText": seasons_text,
            "AlternativeName": movie.get("alternativeName", ""),
            "ShortDescription": movie.get("shortDescription", ""),
            "Votes": movie.get("votes", {}).get("kp", 0) if movie.get("votes") else 0,
            "HasPoster": bool(poster_url),
            "HasDescription": bool(movie.get("description"))
        }

    # ========== СЛУЧАЙНЫЕ ФИЛЬМЫ (БЕЗ КЭША) ==========

    async def get_random_movies(self, count: int = 5) -> List[dict]:
        """Получение случайных фильмов - КАЖДЫЙ РАЗ НОВЫЙ ПОИСК"""
        all_movies = []
        page = random.randint(1, 5)

        print(f"Поиск {count} случайных фильмов на странице {page}...")

        params = {
            "page": page,
            "limit": 50,
            "type": "movie",
            "notNullFields": ["name", "poster.url", "description", "rating.kp"]
        }

        data = await self._make_request("/movie", params)
        movies = data.get("docs", [])

        for movie in movies:
            if (movie.get("poster") and movie["poster"].get("url") and
                    movie.get("description") and len(movie["description"]) > 10 and
                    movie.get("rating") and movie["rating"].get("kp", 0) > 0):
                all_movies.append(movie)

        if len(all_movies) < count:
            params["page"] = page + 1
            data = await self._make_request("/movie", params)
            movies = data.get("docs", [])
            for movie in movies:
                if (movie.get("poster") and movie["poster"].get("url")):
                    all_movies.append(movie)
                    if len(all_movies) >= count * 2:
                        break

        if not all_movies:
            print("Не найдено фильмов, пробуем без фильтрации...")
            params = {
                "page": random.randint(1, 5),
                "limit": 50,
                "type": "movie"
            }
            data = await self._make_request("/movie", params)
            movies = data.get("docs", [])
            for movie in movies:
                if movie.get("poster") and movie["poster"].get("url"):
                    all_movies.append(movie)

        if not all_movies:
            print("Нет фильмов с постерами!")
            return []

        random.shuffle(all_movies)
        selected = all_movies[:count]
        result = [self._convert_to_wpf_format(m) for m in selected]

        print(f"Найдено {len(all_movies)} фильмов, возвращаем {len(result)}")
        return result

    # ========== СЛУЧАЙНЫЕ СЕРИАЛЫ (БЕЗ КЭША) ==========

    async def get_random_series(self, count: int = 5) -> List[dict]:
        """Получение случайных сериалов - КАЖДЫЙ РАЗ НОВЫЙ ПОИСК"""
        all_series = []
        page = random.randint(1, 5)

        print(f"Поиск {count} случайных сериалов на странице {page}...")

        params = {
            "page": page,
            "limit": 50,
            "type": "tv-series",
            "notNullFields": ["name", "poster.url", "description", "rating.kp"]
        }

        data = await self._make_request("/movie", params)
        series = data.get("docs", [])

        for s in series:
            if (s.get("poster") and s["poster"].get("url") and
                    s.get("description") and len(s["description"]) > 10 and
                    s.get("rating") and s["rating"].get("kp", 0) > 0):
                all_series.append(s)

        if len(all_series) < count:
            params["page"] = page + 1
            data = await self._make_request("/movie", params)
            series = data.get("docs", [])
            for s in series:
                if (s.get("poster") and s["poster"].get("url")):
                    all_series.append(s)
                    if len(all_series) >= count * 2:
                        break

        if not all_series:
            print("Не найдено сериалов, пробуем без фильтрации...")
            params = {
                "page": random.randint(1, 5),
                "limit": 50,
                "type": "tv-series"
            }
            data = await self._make_request("/movie", params)
            series = data.get("docs", [])
            for s in series:
                if s.get("poster") and s["poster"].get("url"):
                    all_series.append(s)

        if not all_series:
            print("Нет сериалов с постерами!")
            return []

        random.shuffle(all_series)
        selected = all_series[:count]
        result = [self._convert_to_wpf_format(s) for s in selected]

        print(f"Найдено {len(all_series)} сериалов, возвращаем {len(result)}")
        return result

    # ========== ПОИСК ПО АКТЕРУ ==========

    async def search_by_actor(self, actor_name: str, limit: int = 100) -> List[dict]:
        """Поиск всех фильмов по актеру"""
        cache_key = f"actor_{actor_name}_{limit}"

        cached = self.search_cache.get(cache_key)
        if cached:
            return cached

        all_movies = []
        page = 1

        print(f"Поиск фильмов с актером: {actor_name}")

        while page <= 10:
            params = {
                "page": page,
                "limit": 100,
                "persons.name": actor_name,
                "notNullFields": ["poster.url", "description"]
            }

            data = await self._make_request("/movie", params)
            movies = data.get("docs", [])

            if not movies:
                break

            for movie in movies:
                if movie.get("poster") and movie["poster"].get("url"):
                    all_movies.append(movie)

            print(f"Страница {page}: найдено {len(movies)} фильмов")
            page += 1
            await asyncio.sleep(0.1)

        seen_ids = set()
        unique_movies = []
        for movie in all_movies:
            if movie["id"] not in seen_ids:
                seen_ids.add(movie["id"])
                unique_movies.append(movie)

        result = [self._convert_to_wpf_format(m) for m in unique_movies]
        result.sort(key=lambda x: x.get("Rating", 0) or 0, reverse=True)

        print(f"Найдено уникальных фильмов: {len(result)}")
        self.search_cache.set(cache_key, result[:limit])
        return result[:limit]

    # ========== ПОИСК ПО НАЗВАНИЮ ==========

    async def search_by_name(self, query: str, limit: int = 20) -> List[dict]:
        """Поиск фильмов по названию"""
        cache_key = f"name_{query}_{limit}"

        cached = self.search_cache.get(cache_key)
        if cached:
            return cached

        print(f"\n🔍 Поиск по названию: '{query}'")

        if len(query) < 2:
            return []

        params = {
            "page": 1,
            "limit": limit,
            "query": query,
            "selectFields": ["id", "name", "description", "year", "rating",
                             "poster", "genres", "countries", "movieLength",
                             "type", "ageRating", "alternativeName"],
            "notNullFields": ["poster.url", "description"]
        }

        data = await self._make_request("/movie/search", params)

        if not data or not data.get('docs'):
            print(f"  Ничего не найдено для '{query}'")
            return []

        content_list = data.get('docs', [])
        print(f"  Найдено фильмов в ответе: {len(content_list)}")

        matching_content = []
        query_lower = query.lower().strip()

        for content in content_list:
            if content.get('id') and content.get('name'):
                content_title = content.get('name', '').lower().strip()
                if content_title == query_lower or query_lower in content_title:
                    matching_content.append(content)

        matching_content = matching_content[:limit]

        print(f"  После фильтрации: {len(matching_content)} фильмов")

        if not matching_content:
            return []

        result = [self._convert_to_wpf_format(m) for m in matching_content]
        print(f"  Возвращаем {len(result)} фильмов")

        self.search_cache.set(cache_key, result)
        return result

    # ========== ПОИСК ПО ФИЛЬТРУ (с фильтрацией постера и описания) ==========

    async def search_by_filter(
            self,
            genre: Optional[str] = None,
            year_from: Optional[int] = None,
            year_to: Optional[int] = None,
            rating_from: Optional[float] = None,
            rating_to: Optional[float] = None,
            country: Optional[str] = None,
            limit: int = 100
    ) -> List[dict]:
        """Поиск фильмов по фильтру (только с постерами и описанием)"""
        cache_key = f"filter_{genre}_{year_from}_{year_to}_{rating_from}_{rating_to}_{country}_{limit}"

        cached = self.search_cache.get(cache_key)
        if cached:
            return cached

        params = {
            "page": 1,
            "limit": limit * 2,
            "notNullFields": ["poster.url", "description"]
        }

        if genre:
            params["genres.name"] = genre

        if year_from and year_to:
            params["year"] = f"{year_from}-{year_to}"
        elif year_from:
            params["year"] = f"{year_from}-2025"
        elif year_to:
            params["year"] = f"1900-{year_to}"

        if rating_from and rating_to:
            params["rating.kp"] = f"{rating_from}-{rating_to}"
        elif rating_from:
            params["rating.kp"] = f"{rating_from}-10"
        elif rating_to:
            params["rating.kp"] = f"0-{rating_to}"

        if country:
            params["countries.name"] = country

        data = await self._make_request("/movie", params)
        movies = data.get("docs", [])

        # Дополнительная фильтрация
        valid_movies = []
        for movie in movies:
            if (movie.get("poster") and movie["poster"].get("url") and
                    movie.get("description") and len(movie["description"]) > 20):
                valid_movies.append(movie)

        result = [self._convert_to_wpf_format(m) for m in valid_movies[:limit]]
        result.sort(key=lambda x: x.get("Rating", 0) or 0, reverse=True)

        print(f"По фильтру найдено {len(result)} фильмов с постерами и описанием")
        self.search_cache.set(cache_key, result)
        return result

    # ========== ПОЛУЧЕНИЕ ФИЛЬМА ПО ID ==========

    async def get_movie_by_id(self, movie_id: int) -> Optional[dict]:
        """Получение фильма по ID"""
        cached = self.movies_cache.get(movie_id)
        if cached:
            return cached

        data = await self._make_request(f"/movie/{movie_id}")
        if data and data.get("id"):
            movie = self._convert_to_wpf_format(data)
            self.movies_cache.set(movie_id, movie)
            return movie
        return None

    # ========== МЕТОДЫ ДЛЯ ПОДБОРОК ==========

    def get_collections(self) -> List[dict]:
        return self.my_collections

    def add_to_collection(self, movie_id: int, collection_name: str) -> bool:
        collection = next((c for c in self.my_collections if c["name"] == collection_name), None)
        if not collection:
            collection = {"name": collection_name, "movies": []}
            self.my_collections.append(collection)
        if movie_id not in collection["movies"]:
            collection["movies"].append(movie_id)
            return True
        return False

    def create_collection(self, name: str) -> bool:
        if not next((c for c in self.my_collections if c["name"] == name), None):
            self.my_collections.append({"name": name, "movies": []})
            return True
        return False

    def remove_from_collection(self, collection_name: str, movie_id: int) -> bool:
        collection = next((c for c in self.my_collections if c["name"] == collection_name), None)
        if collection and movie_id in collection["movies"]:
            collection["movies"].remove(movie_id)
            return True
        return False


# Инициализация API
kinopoisk_api = KinopoiskAPI(os.getenv("KINOPOISK_API_TOKEN", "CHHSWYQ-MGZ413R-K8A2STZ-RH7AD6R"))


# ===== ЭНДПОИНТЫ =====

@app.get("/")
async def root():
    return {"message": "Kinopoisk API работает"}


@app.get("/api/random-movie")
async def get_random_movies():
    try:
        movies = await kinopoisk_api.get_random_movies(5)
        print(f"GET /api/random-movie: возвращаем {len(movies)} фильмов")
        return movies
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


@app.get("/api/random-series")
async def get_random_series():
    try:
        series = await kinopoisk_api.get_random_series(5)
        print(f"GET /api/random-series: возвращаем {len(series)} сериалов")
        return series
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


@app.get("/api/search/actor")
async def search_by_actor(
        name: str = Query(..., description="Имя актера"),
        limit: int = Query(100, description="Количество результатов")
):
    try:
        movies = await kinopoisk_api.search_by_actor(name, limit)
        print(f"GET /api/search/actor: найдено {len(movies)} фильмов с {name}")
        return movies
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


@app.get("/api/search/name")
async def search_by_name(
        query: str = Query(..., description="Название фильма"),
        limit: int = Query(20, description="Количество результатов")
):
    try:
        movies = await kinopoisk_api.search_by_name(query, limit)
        print(f"GET /api/search/name: найдено {len(movies)} фильмов по запросу '{query}'")
        return movies
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


@app.get("/api/search/filter")
async def search_by_filter(
        genre: Optional[str] = Query(None, description="Жанр"),
        year_from: Optional[int] = Query(None, description="Год с"),
        year_to: Optional[int] = Query(None, description="Год по"),
        rating_from: Optional[float] = Query(None, description="Рейтинг от"),
        rating_to: Optional[float] = Query(None, description="Рейтинг до"),
        country: Optional[str] = Query(None, description="Страна"),
        limit: int = Query(100, description="Количество результатов")
):
    try:
        movies = await kinopoisk_api.search_by_filter(
            genre=genre,
            year_from=year_from,
            year_to=year_to,
            rating_from=rating_from,
            rating_to=rating_to,
            country=country,
            limit=limit
        )
        print(f"GET /api/search/filter: найдено {len(movies)} фильмов")
        return movies
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


@app.get("/api/movie/{movie_id}")
async def get_movie_by_id(movie_id: int):
    try:
        movie = await kinopoisk_api.get_movie_by_id(movie_id)
        if movie:
            print(f"GET /api/movie/{movie_id}: найден фильм {movie.get('Name')}")
            return movie
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# ПОДБОРКИ
@app.get("/api/collections")
async def get_collections():
    return kinopoisk_api.get_collections()


@app.post("/api/collections/create")
async def create_collection(name: str = Query(...)):
    success = kinopoisk_api.create_collection(name)
    return {"success": success}


@app.post("/api/collections/add")
async def add_to_collection(
        movie_id: int = Query(...),
        collection_name: str = Query(...)
):
    success = kinopoisk_api.add_to_collection(movie_id, collection_name)
    return {"success": success}


@app.delete("/api/collections/remove")
async def remove_from_collection(
        name: str = Query(...),
        movie_id: int = Query(...)
):
    success = kinopoisk_api.remove_from_collection(name, movie_id)
    return {"success": success}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)