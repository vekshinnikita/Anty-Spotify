from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Form, Header, Depends
from ormar.exceptions import NoMatch
from fastapi.responses import Response
from typing import List

from auth.schemas import User
from auth.auth import current_user
from .models import MyMusics
from music.models import Music
from .schemas import GetMyMusic


playlists_router = APIRouter(prefix='/playlists', tags=["user"])


@playlists_router.post("/mymusic", status_code=200)
async def add__or_remove_to_my_musics(
    music_pk: int = Form(...),
    user: User = Depends(current_user)
):  
    try:
        music = await Music.objects.get(pk=music_pk)
    except NoMatch:
        raise HTTPException(status_code=404, detail="Music not found ")
    
    try:
        my_musics = await MyMusics.objects.prefetch_related('musics').get(user__id=user.id)
    except NoMatch:
        my_musics = await MyMusics.objects.create(user=user.id)

    if not music in my_musics.musics:
        await my_musics.musics.add(music)
        detail = 'Successful add'
    else:
        await my_musics.musics.remove(music)
        detail = 'Successful delete'
    

    return {'detail': detail}


@playlists_router.get("/mymusic", response_model=GetMyMusic)
async def get_my_musics(
    user: User = Depends(current_user)
):
    try:
        my_musics = await MyMusics.objects.prefetch_related(['musics', 'musics__poster']).get(user__id=user.id)
    except NoMatch:
        my_musics = await MyMusics.objects.create(user=user.id)

    print(my_musics)
    

    return my_musics

