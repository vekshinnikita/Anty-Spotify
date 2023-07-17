from fastapi import APIRouter, Query, APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Form, Header, Depends
from typing import List
from pydantic import EmailStr
from yandex_music import Client, TracksList
from ormar.exceptions import NoMatch
from uuid import uuid4

from .schemas import UserSchema
from .auth import auth_backend, fastapi_users, SECRET, current_user
from .user_manager import yandex_oauth_client
from .models import OAuthAccount

from music.schemas import UploadMusic
from music.models import Track, Poster, Music
from playlists.models import MyMusics

user_router = APIRouter()

user_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
user_router.include_router(
    fastapi_users.get_register_router(), prefix="/auth", tags=["auth"]
)

user_router.include_router(
  fastapi_users.get_oauth_router(yandex_oauth_client, auth_backend, SECRET),
  prefix="/auth/yandex",
  tags=["auth"],
)

@user_router.get("/get/playlists/list", status_code=200)
async def get_user_yandex_playlists(
    background_task: BackgroundTasks,
    user: UserSchema = Depends(current_user)
):
    try:
        yandex_oauth = await OAuthAccount.objects.get(user__id=user.id, oauth_name='yandex')
    except NoMatch:
        raise HTTPException(status_code=400, detail="You don't authorized by Yandex")

    client = Client('y0_AgAAAAAilvGlAAG8XgAAAADbREwL3I25zzYqQHKSx4gkHUqQZhKerzI').init()
    user_playlists = client.users_playlists_list(user_id=yandex_oauth.username) 

    playlists = [
        {
            "kind": 3,
            "title": "Мне нравится",
            "og_image": "music.yandex.ru/blocks/playlist-cover/playlist-cover_like_2x.png",
        },
    ]

    for i in user_playlists:
        playlists.append({
            "kind": i['kind'],
            "title": i['title'],
            "og_image": i['og_image'],
        })
    

    return playlists

@user_router.post("/transfer/playlist", status_code=200)
async def get_user_yandex_playlists(
    background_task: BackgroundTasks,
    user: UserSchema = Depends(current_user),
    kind: int = Form(...)
    
):

    try:
        yandex_oauth = await OAuthAccount.objects.get(user__id=user.id, oauth_name='yandex')
    except NoMatch:
        raise HTTPException(status_code=400, detail="You don't authorized by Yandex")

    client = Client('y0_AgAAAAAilvGlAAG8XgAAAADbREwL3I25zzYqQHKSx4gkHUqQZhKerzI').init()
    playlist = client.users_playlists(kind, user_id=yandex_oauth.username)

    client.users_likes_tracks()

    background_task.add_task(save_playlist_yandex, playlist['tracks'], user)


    return 'Ok'


async def save_playlist_yandex(playlist: TracksList, user: UserSchema):

    try:
        my_musics = await MyMusics.objects.prefetch_related('musics').get(user__id=user.id)
    except NoMatch:
        my_musics = await MyMusics.objects.create(user=user.id)

    for track in playlist:
        file_name_music = f'media/musics/{uuid4()}.mp3'
        track.fetch_track().download(file_name_music)

        authors = []

        for artist in track.track.artists:
            authors.append(artist.name)

        info = UploadMusic(title=track.track.title, author=' & '.join(authors))

        track_obj = await Track.objects.create(content_type='audio/mp3', path=file_name_music)
        poster_obj = await Poster.objects.create(content_type='image/jpeg', path=track.track.cover_uri, local=0)

        music = await Music.objects.create(track=track_obj, poster=poster_obj, user=user.dict(), **info.dict())

        await my_musics.musics.add(music)