from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from kinopoisk_client import get_random_series

app = FastAPI(
    title="Kinopoisk Random Series API",
    description="API для получения случайных сериалов с Кинопоиска",
    version="1.0.0"
)

class Series(BaseModel):
    id: int
    name: str
    description: str
    posterUrl: str

@app.get("/")
async def root():
    return {"message": "Kinopoisk Random Series API Server", "status": "running"}

@app.get("/api/random-series", response_model=List[Series])
async def api_get_random_series():
    try:
        series = get_random_series(limit=5)
        return series
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)