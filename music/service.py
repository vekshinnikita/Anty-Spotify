import shutil
from fastapi import UploadFile, BackgroundTasks, HTTPException, Depends
from uuid import uuid4
import ormar
from typing import IO, Generator
from pathlib import Path
from starlette.requests import Request 
from PIL import Image
from io import BytesIO

from .schemas import UploadMusic
from .models import Music, Track, Poster
from auth.schemas import UserSchema, User


async def save_music(
        file: UploadFile,
        poster: UploadFile,
        title: str,
        author: str,
        back_tasks: BackgroundTasks,
        user: UserSchema
):
    file_name_music = f'media/musics/{uuid4()}'
    file_name_poster = f'media/posters/{uuid4()}'

    file_type = file.content_type.split('/')

    if file_type[0] == 'audio':
        file_name_music =f'{file_name_music}.{file_type[1]}'
        back_tasks.add_task(write_music, file_name_music, file)
    else:
        raise HTTPException(status_code=418, detail="File isn't audio")
    
    poster_type = poster.content_type.split('/')

    if poster_type[0] == 'image':
        file_name_poster = f'{file_name_poster}.{poster_type[1]}'
        back_tasks.add_task(write_poster, file_name_poster, poster)
    else:
        raise HTTPException(status_code=418, detail="Poster isn't image")

    
    info = UploadMusic(title=title, author=author)

    track_obj = await Track.objects.create(content_type=file.content_type, path=file_name_music)
    poster_obj = await Poster.objects.create(content_type=poster.content_type, path=file_name_poster)

    return await Music.objects.create(track=track_obj, poster=poster_obj, user=user.dict(), **info.dict())

def cut_resize_img(img: Image) -> Image:

    width, height = img.size

    if width < height:
        max_is_height = True
    else:
        max_is_height = False

    mid_height = int(height/2)
    mid_width = int(width/2)

    if max_is_height:
        y1 = mid_height - mid_width
        y2 = mid_height + mid_width
        x1 = 0
        x2 = width
    else:
        x1 = mid_width - mid_height
        x2 = mid_width + mid_height
        y1 = 0
        y2 = height
    
    new_image = img.crop((x1,y1,x2,y2))

    return new_image.resize((100,100))


async def write_music(file_name: str, file: UploadFile):
    
    with open(file_name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

async def write_poster(file_name: str, file: Image):
    img = cut_resize_img(Image.open(file.file))
    img.save(file_name)


def ranged(
        file: IO[bytes],
        start: int = 0,
        end: int = None,
        block_size: int = 8192,
) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)
    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size
        if data_length <= 0:
            break
        data = file.read(data_length)
        if not data:
            break
        consumed += data_length
        yield data

    if hasattr(file, 'close'):
        file.close()


async def open_file_range(
    request: Request, 
    video_pk: int,
    type: str = 'track'
    ) -> tuple:
    try:
        file = await Music.objects.select_related(type).get(pk=video_pk)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="Not found")
    
    dict = file.dict().get(type)
    content_type = dict.get('content_type')
    path = Path(dict.get('path'))


    file = path.open('rb')

    file_size = path.stat().st_size

    content_length = file_size
    status_code = 200
    headers = {}
    content_range = request.headers.get('range')

    if content_range is not None:
        content_range = content_range.strip().lower()
        content_ranges = content_range.split('=')[-1]
        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))
        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1
        content_length = (range_end - range_start) + 1
        file = ranged(file, start=range_start, end=range_end + 1)
        status_code = 206
        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    return file,content_type, status_code, headers, content_length


async def open_file(
    video_pk: int,
    type: str = 'track'
    ) -> tuple:
    try:
        file = await Music.objects.select_related(type).get(pk=video_pk)
    except ormar.exceptions.NoMatch:
        raise HTTPException(status_code=404, detail="Not found")
    
    dict = file.dict().get(type)
    content_type = dict.get('content_type')
    path = Path(dict.get('path'))


    file = path.open('rb')

    status_code = 200


    return file, content_type, status_code