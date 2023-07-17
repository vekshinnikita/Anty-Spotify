from fastapi import FastAPI
from music.api import music_router
from auth.routers import user_router
from playlists.api import playlists_router
from db import metadata, database, engine


app = FastAPI()

metadata.create_all(engine)
app.state.database = database


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


app.include_router(music_router)
app.include_router(user_router)
app.include_router(playlists_router)
