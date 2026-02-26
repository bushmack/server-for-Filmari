from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TOKEN = "859EJFM-R0HMPJK-Q038VE6-QMXJVWP"
HEADERS = {"X-API-KEY": TOKEN}


# ========== СЛУЧАЙНЫЕ ФИЛЬМЫ ==========
@app.get("/api/random-movie")
async def random_movies():
    try:
        print("\n=== ПОИСК ФИЛЬМОВ ===")
        all_movies = []

        # Собираем с 5 страниц
        for page in range(1, 6):
            response = requests.get(
                "https://api.kinopoisk.dev/v1.4/movie",
                headers=HEADERS,
                params={
                    "page": page,
                    "limit": 50,
                    "type": "movie"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                movies = data.get("docs", [])
                print(f"Страница {page}: получили {len(movies)} фильмов")

                # ТОЛЬКО ДВЕ ПРОВЕРКИ: постер и описание
                for m in movies:
                    if (m.get("poster") and m["poster"].get("url") and
                        m.get("description")):
                        all_movies.append(m)
            else:
                print(f"Ошибка API: {response.status_code}")

        print(f"Всего фильмов с постером и описанием: {len(all_movies)}")

        if not all_movies:
            print("НЕТ ПОДХОДЯЩИХ ФИЛЬМОВ!")
            return JSONResponse(content=[])

        # Перемешиваем
        random.shuffle(all_movies)

        # Берем первые 5
        result = []
        for m in all_movies[:5]:
            # Название
            name = m.get("name") or m.get("alternativeName") or "Без названия"

            # Описание (точно есть)
            description = m["description"]

            # Постер (точно есть)
            poster = m["poster"]["url"]

            # Жанр
            genre = ""
            if m.get("genres") and len(m["genres"]) > 0:
                genre = m["genres"][0].get("name", "")

            # Год
            year = m.get("year")

            # Рейтинг (пофиг какой)
            rating = 0.0
            if m.get("rating"):
                rating = m["rating"].get("kp") or m["rating"].get("imdb") or 0.0

            movie_data = {
                "Id": int(m.get("id", 0)),
                "Name": name,
                "Description": description,
                "PosterUrl": poster,
                "Year": year,
                "Genre": genre,
                "Rating": round(float(rating), 1) if rating else 0
            }

            print(f"ДОБАВЛЕН: {name}")
            result.append(movie_data)

        print(f"ИТОГО: {len(result)} фильмов")
        return JSONResponse(content=result)

    except Exception as e:
        print(f"ОШИБКА: {e}")
        return JSONResponse(content=[])


# ========== СЛУЧАЙНЫЕ СЕРИАЛЫ ==========
@app.get("/api/random-series")
async def random_series():
    try:
        print("\n=== ПОИСК СЕРИАЛОВ ===")
        all_series = []

        for page in range(1, 4):
            response = requests.get(
                "https://api.kinopoisk.dev/v1.4/movie",
                headers=HEADERS,
                params={
                    "page": page,
                    "limit": 50,
                    "type": "tv-series",
                    "selectFields": ["id", "name", "description", "shortDescription",
                                     "year", "rating", "poster", "genres"],
                    "notNullFields": ["name", "poster.url", "description", "rating.kp"]
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                series = data.get("docs", [])

                for s in series:
                    if (s.get("poster") and s["poster"].get("url") and
                            s.get("description") and
                            s.get("rating") and s["rating"].get("kp", 0) > 0):
                        all_series.append(s)

        if not all_series:
            return JSONResponse(content=[])

        random.shuffle(all_series)

        result = []
        for s in all_series[:5]:
            rating = s["rating"]["kp"]
            result.append({
                "Id": int(s["id"]),
                "Name": s.get("name") or s.get("alternativeName", "Без названия"),
                "Description": s["description"],
                "PosterUrl": s["poster"]["url"],
                "Year": s.get("year"),
                "Genre": s.get("genres", [{}])[0].get("name", "") if s.get("genres") else "",
                "Rating": round(float(rating), 1)
            })

        return JSONResponse(content=result)

    except Exception as e:
        print(f"Ошибка: {e}")
        return JSONResponse(content=[])


@app.get("/")
async def root():
    return {"message": "Kinopoisk API работает"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)