from pydantic import BaseModel, validator
from typing import Optional
from auth.schemas import User
from env import BASE_URL

class UploadMusic(BaseModel):
    title: str
    author: str

class Track(BaseModel):
    id: int
    url: Optional[str] = None

    @validator('url', always=True)
    def ab(cls, v, values: dict) -> str:
        return f"{BASE_URL}/track/music/{values.get('id', None)}"

class Poster(BaseModel):
    id: int
    local: int
    path: str
    url: Optional[str] = None

    @validator('url', always=True)
    def ab(cls, v, values: dict) -> str:
        if values.get('local', None) == 0:
            return f"https://{values.get('path', None)}"

        return f"{BASE_URL}/track/poster/{values.get('id', None)}"

class GetMusic(BaseModel):
    title: str
    author: str
    poster: Poster
    track: Track
    user: User
    views_count: int

