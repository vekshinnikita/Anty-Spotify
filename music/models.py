import ormar
import datetime
from db import MainMeta
from typing import Optional, Union, Dict, List
from auth.models import User
from auth.schemas import UserSchema



class Poster(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    path: str = ormar.String(max_length=1000)
    content_type: str = ormar.String(max_length=1000)
    local: Optional[int] = ormar.Integer(default=1)

class Track(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    path: str = ormar.String(max_length=1000)
    content_type: str = ormar.String(max_length=1000)

class Music(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    title: str = ormar.String(max_length=150)
    author: str = ormar.String(max_length=150)
    create_at: datetime.datetime = ormar.DateTime(default=datetime.datetime.now)
    poster: Optional[Union[Poster, Dict]] = ormar.ForeignKey(Poster, related_name="poster")
    track: Optional[Union[Track, Dict]] = ormar.ForeignKey(Track, related_name="track")
    views_count:int = ormar.Integer(default=0) 
    user: Union[UserSchema, Dict] = ormar.ForeignKey(User)