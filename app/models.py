# app/models.py
from __future__ import annotations

import uuid
from typing import Optional, List
from datetime import datetime, UTC

from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, UniqueConstraint
from sqlalchemy.types import Enum as SQLAlchemyEnum
import enum


# ───────────────────────── Users (CURRENT) ─────────────────────────
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fullname: str = Field(min_length=2)
    phone: str = Field(unique=True, index=True)
    password: str = Field()                         # хранить хэш
    role: str = Field(default="user")               # "user" | "admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


# ───────────────────────── Videos (CURRENT) ────────────────────────
class VideoStatus(str, enum.Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"


class Video(SQLModel, table=True):
    __tablename__ = "video"

    id: str = Field(primary_key=True, index=True)   # uuid как строка
    title: str
    description: str
    preview_img: str                                 # s3 key
    video: str                                       # s3 key
    status: VideoStatus = Field(default=VideoStatus.ACTIVE)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deleted_at: Optional[datetime] = Field(default=None)


# ───────────────────────── Books (CURRENT, ТЗ) ─────────────────────
class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)

    # core
    title: str = Field(min_length=1, index=True, nullable=False)
    author: str = Field(min_length=1, index=True, nullable=False)
    description: str = Field(nullable=False)
    genre: Optional[str] = Field(default=None, index=True)

    # storage links
    file_url: str = Field(nullable=False)           # pdf/epub
    cover_url: Optional[str] = Field(default=None)  # обложка

    # meta
    published_year: Optional[int] = Field(default=None, ge=0, le=2100)

    # audit
    created_by: uuid.UUID = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


# ───────────────────────── Playlist / Music / Genre (INCOMING) ────
class Playlist(SQLModel, table=True):
    __tablename__ = "playlist"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    description: str
    preview_img: str
    musics: List["Music"] = Relationship(back_populates="playlist", cascade_delete=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    )
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class MusicStatus(str, enum.Enum):
    ACTIVE = "active"
    PROCESSING = "processing"
    FAILED = "failed"


class GenreType(str, enum.Enum):
    MUSIC = "music"
    MOVIE = "movie"
    BOOK = "book"


class Genre(SQLModel, table=True):
    __tablename__ = "genre"
    __table_args__ = (
        UniqueConstraint("name", "type", name="uq_genre_name_type"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=100)
    description: Optional[str] = None
    type: GenreType = Field(sa_column=Column(SQLAlchemyEnum(GenreType, name="genre_type_enum"), nullable=False))

    musics: List["Music"] = Relationship(back_populates="genre")

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    )
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class Music(SQLModel, table=True):
    __tablename__ = "music"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    playlist_id: uuid.UUID = Field(foreign_key="playlist.id", nullable=False)
    playlist: Optional[Playlist] = Relationship(back_populates="musics")

    genre_id: Optional[uuid.UUID] = Field(default=None, foreign_key="genre.id", nullable=True)
    genre: Optional[Genre] = Relationship(back_populates="musics")

    status: MusicStatus = Field(sa_column=Column(SQLAlchemyEnum(MusicStatus, name="music_status_enum")), default=MusicStatus.PROCESSING)
    title: str
    description: str
    preview_img: str
    music_url: str
    duration: int

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    )
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


# ───────────────────────── Ads / Statistics (INCOMING) ────────────
class AdStatus(str, enum.Enum):
    ACTIVE = "active"
    PROCESSING = "processing"
    FAILED = "failed"


class Ad(SQLModel, table=True):
    __tablename__ = "ad"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    video_url: str
    status: AdStatus = Field(sa_column=Column(SQLAlchemyEnum(AdStatus, name="ad_status_enum")), default=AdStatus.PROCESSING)

    statistics: List["Statistics"] = Relationship(back_populates="ad", cascade_delete=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC))
    )
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)


class Statistics(SQLModel, table=True):
    __tablename__ = "statistics"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    device_id: uuid.UUID

    ad_id: uuid.UUID = Field(foreign_key="ad.id", nullable=False)
    ad: Ad = Relationship(back_populates="statistics")

    watched_full: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
