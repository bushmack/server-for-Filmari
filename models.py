from pydantic import BaseModel
from typing import List, Optional


class Country(BaseModel):
    name: str


class Genre(BaseModel):
    name: str


class Film(BaseModel):
    id: int
    name: Optional[str] = None
    alternativeName: Optional[str] = None
    year: Optional[int] = None
    description: Optional[str] = None
    rating: Optional[dict] = None
    poster: Optional[dict] = None
    countries: Optional[List[Country]] = None
    genres: Optional[List[Genre]] = None
    movieLength: Optional[int] = None
    ageRating: Optional[int] = None


class RandomFilmsResponse(BaseModel):
    films: List[Film]
    count: int