from pydantic import BaseModel
from typing import List

from auth.schemas import User
from music.schemas import GetMusic


class GetMyMusic(BaseModel):
    musics: List[GetMusic]
