from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from typing import Optional, List
import uuid

from app.core.db import get_session
from app.models import GenreType
from app.schemas import GenrePublic, GenreCreate, GenreUpdate
from app.modules.genre.genre_service import GenreService

genre_router = APIRouter(prefix="/genres", tags=["Genres"])
service = GenreService()

@genre_router.get("/", response_model=List[GenrePublic])
def get_genres(
    skip: Optional[int] = Query(default=None, ge=0),
    limit: Optional[int] = Query(default=None, ge=1),
    q: Optional[str] = Query(default=None),
    type: Optional[GenreType] = Query(default=None),
    sort_by: Optional[str] = Query(default="created_at"),
    order: Optional[str] = Query(default="asc", regex="^(asc|desc)$"),
):
    return service.get_all(skip=skip, limit=limit, q=q, type=type, sort_by=sort_by, order=order)

@genre_router.get("/{genre_id}", response_model=GenrePublic)
def get_genre(genre_id: uuid.UUID):
    return service.get_by_id(genre_id)


@genre_router.post("/", response_model=GenrePublic)
def create_genre(data: GenreCreate):
    return service.create(data)


@genre_router.put("/{genre_id}", response_model=GenrePublic)
def update_genre(genre_id: uuid.UUID, data: GenreUpdate):
    return service.update(genre_id, data)


@genre_router.delete("/{genre_id}", response_model=GenrePublic)
def delete_genre(genre_id: uuid.UUID):
    return service.delete(genre_id)
