from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .enums import VideoStatus

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
