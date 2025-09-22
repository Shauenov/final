# app/schemas.py (только блок users)
from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.modules.videos.enums import VideoStatus  # импорт ТОЛЬКО enum

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
