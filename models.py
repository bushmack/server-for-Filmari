from pydantic import BaseModel
from typing import List, Optional

class Film(BaseModel):
    id: int
    name: str
    description: str
    posterUrl: str
    year: Optional[int] = None
    genre: Optional[str] = None
    rating: Optional[float] = None

class UserCollection(BaseModel):
    user_id: str
    films: List[Film]