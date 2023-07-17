from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Form, Header, Depends
from starlette.requests import Request
from starlette.responses import StreamingResponse
import os
from typing import List
from pydantic import UUID4

from .service import save_music, open_file, open_file_range
from .schemas import GetMusic
from .models import Music, Track
from auth.schemas import UserSchema, User
from auth.auth import current_user
from env import BASE_URL

music_router = APIRouter(prefix='/track', tags=["track"])


@music_router.post("/music", response_model=GetMusic)
async def create_music(
    back_tasks: BackgroundTasks,
    poster: UploadFile = File(...),
    title: str = Form(...),
    author: str = Form(...),
    file: UploadFile = File(...),
    user: UserSchema = Depends(current_user)
):
    return await save_music(file, poster, title, author, back_tasks, user)


@music_router.get("/music/{music_pk}")
async def striaming_music(
    request: Request,
    music_pk: int,
) -> StreamingResponse :

    first_load = not bool(request.headers.get('range'))
    
    if first_load: 
        # count views 
        music = await Music.objects.get(pk=music_pk)
        music.views_count += 1
        await music.update()

    file, content_type, status_code, headers, content_length = await open_file_range(request, music_pk)

    response = StreamingResponse(
        file,
        media_type=content_type,
        status_code=status_code,
    )

    response.headers.update({
        'Accept-Ranges': 'bytes',
        'Content-Length': str(content_length),
        **headers,
    })
    return response


@music_router.get("/poster/{pk}")
async def get_poster(
    pk: int,
    
) -> StreamingResponse :
    file, content_type, status_code = await open_file(pk, 'poster')

    response = StreamingResponse(
        file,
        media_type=content_type,
        status_code=status_code,
    )
    return response


@music_router.get("/user/{user_pk}", response_model=List[GetMusic] )
async def get_user_track(
    user_pk: UUID4,
):

    data = await Music.objects.select_related('poster').filter(user=user_pk).all()

    return data




@music_router.get("/{track_pk}", response_model=GetMusic)
async def get_track(
    request: Request,
    track_pk: int,
):
    data = await Music.objects.select_related(['user', 'poster']).get(pk=track_pk)

    return data


    