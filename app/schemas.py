# app/schemas.py (только блок users)
from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.modules.videos.video_repository import VideoStatus  # импорт ТОЛЬКО enum

PHONE_RE = r"^\+7\d{10}$"

class CreateUser(BaseModel):
    fullname: str = Field(min_length=2)
    phone: str = Field(pattern=PHONE_RE)
    password: str = Field(min_length=8)
    role: Optional[str] = Field(default="user")

class UpdateUser(BaseModel):
    fullname: Optional[str] = Field(default=None, min_length=2)
    phone: Optional[str] = Field(default=None, pattern=PHONE_RE)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[str] = Field(default=None)

class UserPublic(BaseModel):
    id: uuid.UUID
    fullname: str
    phone: str
    role: str
    class Config:
        from_attributes = True


class CreatePlaylist(BaseModel):
  title: str = Field()
  description: str = Field()
  preview_img: str = Field()

class UpdatePlaylist(BaseModel):
  title: Optional[str] = Field(default=None)
  description: Optional[str] = Field(default=None)

class PlaylistPublic(BaseModel):
  id: uuid.UUID = Field()
  title: str = Field()
  description: str = Field()
  preview_img: str = Field()
  musics: list["MusicPublic"] = []
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = Field(nullable=True)

  class Config:
      from_attributes = True

class CreateMusic(BaseModel):
  title: str = Field()
  playlist_id: str = Field()
  description: str = Field()
  preview_img: str = Field()
  music_url: str = Field()
  duration: int = Field()


class UpdateMusic(BaseModel):
  title: Optional[str] = Field(default=None)
  description: Optional[str] = Field(default=None)
  music_url: Optional[str] = Field(default=None)

class MusicPublic(BaseModel):
  id: uuid.UUID = Field()
  title: str = Field()
  description: str = Field()
  preview_img: str = Field()
  music_url: str = Field()
  duration: int = Field()
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = Field(nullable=True)

  class Config:
      from_attributes = True


# Videos schemas

class VideoCreate(BaseModel):
    title: str
    description: str

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class VideoOut(BaseModel):
    id: str
    title: str
    description: str
    preview_img: str
    video: str
    status: VideoStatus
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


# Books schemas

class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    description: str
    genre: Optional[str] = None
    published_year: Optional[int] = Field(default=None, ge=0, le=2100)


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    published_year: Optional[int] = Field(default=None, ge=0, le=2100)
    # file_url / cover_url меняются отдельными эндпоинтами через UploadFile


class BookOut(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    description: str
    genre: Optional[str]
    file_url: str
    cover_url: Optional[str]
    published_year: Optional[int]
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # для валидации из ORM-модели SQLModel