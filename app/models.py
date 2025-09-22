import enum
from typing import Optional
import uuid
from datetime import datetime, UTC
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel, UniqueConstraint
from app.modules.videos.enums import VideoStatus  # только enum!
from sqlalchemy.types import Enum as SQLAlchemyEnum
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


# ── Users (по ТЗ: Bearer, телефон+пароль; роли) ───────────────────────────────
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fullname: str = Field(min_length=2)
    phone: str = Field(unique=True, index=True)
    password: str = Field()                    # хранить ХЭШ (bcrypt/argon2), не plain
    role: str = Field(default="user")          # "user" | "admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)  # для soft-delete


class VideoStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"

class Video(SQLModel, table=True):
    __tablename__ = "video"

    id: str = Field(primary_key=True, index=True)                # uuid строкой
    title: str
    description: str
    preview_img: str                                             # s3 key
    video: str                                                   # s3 key
    status: VideoStatus = Field(default=VideoStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None                        # soft delete

class Playlist(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  title: str = Field()
  description: str = Field()
  preview_img: str = Field()
  musics: list["Music"] = Relationship(back_populates="playlist", cascade_delete=True)
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(
      sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
  )
  deleted_at: datetime = Field(default_factory=None, nullable=True)

class MusicStatus(enum.Enum):
  ACTIVE="active"
  PROCESSING="processing"
  FAILED="failed"

class Music(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  playlist_id: uuid.UUID = Field(
    foreign_key="playlist.id", nullable=False, ondelete="CASCADE"
  )
  playlist: Playlist | None = Relationship(
    back_populates="musics"
  )
  genre_id: uuid.UUID | None = Field(
      default=None,
      foreign_key="genre.id",
      nullable=True
  )
  genre: Optional["Genre"] = Relationship(
      back_populates="musics"
  )
  status: MusicStatus = Field(
      sa_column=Column(SQLAlchemyEnum(MusicStatus, name="music_status_enum"))
  )
  title: str = Field()
  description: str = Field()
  preview_img: str = Field()
  music_url: str = Field()
  duration: int = Field()
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(
      sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
  )
  deleted_at: datetime = Field(default_factory=None, nullable=True)

class GenreType(str, enum.Enum):
    MUSIC = "music"
    MOVIE = "movie"
    BOOK = "book"

class Genre(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("name", "type", name="uq_genre_name_type"),
    )
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=100)
    description: Optional[str] = None
    musics: list["Music"] = Relationship(back_populates="genre")
    type: GenreType = Field(
        sa_column=Column(SQLAlchemyEnum(GenreType, name="genre_type_enum"), nullable=False)
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    )
    deleted_at: datetime = Field(default_factory=None, nullable=True)
