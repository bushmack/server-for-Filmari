import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Simple Kinopoisk API")

KINOPOISK_API_KEY = "H974FM6-0V3M4CP-HNA5Q7V-ARMKP1B"

class Series(BaseModel):
    id: int
    name: str
    description: str
    posterUrl: str

@app.get("/")
async def root():
    return {"message": "Simple Kinopoisk API", "status": "running"}

@app.get("/api/random-series", response_model=List[Series])
async def get_random_series():
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
    try:
        response = requests.get("https://kinopoiskapiunofficial.tech/api/v2.2/films", headers=headers, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Ошибка API Кинопоиска")

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
        ][:5]

        return series_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)