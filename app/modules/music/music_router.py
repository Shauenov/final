import uuid
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Form, Path, UploadFile
from pydantic import Field

from app.schemas import MusicPublic
from app.modules.music.music_service import MusicService

service = MusicService()

music_router = APIRouter(
    prefix="/musics",
    tags=["Music"],
)

@music_router.get("/{id}", response_model=MusicPublic | None)
def get_music_by_id(
    id: Annotated[str, Path(description="The id of music")],
):
    return service.findById(id)

@music_router.get("/", response_model=list[MusicPublic])
def get_musics(
    skip: int | None = None,
    limit: int | None = None,
    q: str | None = None,
    playlist_id: uuid.UUID | None = None
):
    return service.findAll(skip=skip, limit=limit, q=q, playlist_id=playlist_id)

@music_router.post("/", response_model=MusicPublic)
async def create_music(
    playlist_id: Annotated[
        uuid.UUID,
        Form(...),
        Field()
    ],
    title: Annotated[
        str,
        Form(...),
        Field()
    ],
    description: Annotated[
        str,
        Form(...),
        Field()
    ],
    preview_img: UploadFile,
    music: UploadFile,
    background_tasks: BackgroundTasks
):
    return await service.create(playlist_id=str(playlist_id), title=title, description=description, preview_img=preview_img, music=music, background_tasks=background_tasks)

@music_router.delete("/{id}", response_model=MusicPublic)
def delete_music(
    id: Annotated[uuid.UUID, Path(description="The id of music")],
):
    return service.deleteById(id)
