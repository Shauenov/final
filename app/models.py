from typing import Optional
import uuid
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel
from app.modules.videos.enums import VideoStatus  # только enum!

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

# VIDEOS- - -  - - -- - - - ---------------


from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field


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
