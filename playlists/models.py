import ormar
import datetime
from db import MainMeta
from typing import Optional, Union, Dict, List

from auth.models import User
from auth.schemas import User as UserShema
from music.models import Music
from music.schemas import GetMusic

class MyMusics(ormar.Model):
    class Meta(MainMeta):
        pass
    
    id: int = ormar.Integer(primary_key=True)
    user: Union[UserShema, Dict] = ormar.ForeignKey(User, related_name='user', unique=True)
    musics: Optional[List[GetMusic]] = ormar.ManyToMany(
        Music
    )   