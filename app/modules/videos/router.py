# app/modules/videos/router.py
from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form, Depends
from sqlmodel import Session, select
from pydantic import BaseModel

# >>> ВАЖНО: бери сессию из ядра проекта (Postgres), а НЕ свой SQLite
from app.core.db import get_session  # если у тебя другое место/имя — подправь импорт

# всё, что ты перенёс из minio-проекта внутрь модуля:
from .s3_client import s3, S3_BUCKET, upload_obj, guess_ct, presign_get
from .utils_media import is_image_stream
from .enums import VideoStatus
from app.models import Video
from .schemas import VideoCreate, VideoUpdate, VideoOut

from fastapi import Depends
from app.modules.auth.auth_router import admin_guard


router = APIRouter(prefix="/videos", tags=["videos"])


# ===== DTO для PATCH (если нужно через JSON, но ниже у нас Form-подход сохранён) =====
class VideoPatch(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[VideoStatus] = None


# ===== Helpers =====
def ensure_exists(session: Session, vid: str) -> Video:
    item = session.get(Video, vid)
    if not item or item.deleted_at:
        raise HTTPException(404, "Video not found")
    return item


# ===== CRUD =====

@router.post("", response_model=VideoOut)
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    preview: UploadFile = File(..., description="preview image"),
    file: UploadFile = File(..., description="video file"),
    session: Session = Depends(get_session),
    _=Depends(admin_guard),
):
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "file must be a video/*")

    # строгая проверка превью по «магическим байтам»
    if not is_image_stream(preview.file, preview.content_type):
        raise HTTPException(400, "preview must be a real image (jpg/png/webp/gif)")

    vid = str(uuid.uuid4())
    preview_ext = os.path.splitext(preview.filename)[1] or ".jpg"
    video_ext   = os.path.splitext(file.filename)[1] or ".mp4"

    preview_key = f"videos/{vid}/preview{preview_ext}"
    video_key   = f"videos/{vid}/source{video_ext}"

    upload_obj(preview.file, preview_key, guess_ct(preview.filename, preview.content_type))
    upload_obj(file.file,    video_key,   guess_ct(file.filename, file.content_type))

    item = Video(
        id=vid,
        title=title,
        description=description,
        preview_img=preview_key,
        video=video_key,
        status=VideoStatus.ACTIVE,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("", response_model=List[VideoOut])
def list_videos(
    status: Optional[VideoStatus] = Query(default=None),
    q: Optional[str] = Query(default=None, description="substring in title/description"),
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    _=Depends(admin_guard),
):
    stmt = select(Video).where(Video.deleted_at.is_(None))
    if status:
        stmt = stmt.where(Video.status == status)
    if q:
        like = f"%{q}%"
        stmt = stmt.where((Video.title.like(like)) | (Video.description.like(like)))
    stmt = stmt.order_by(Video.created_at.desc()).limit(limit).offset(offset)
    return session.exec(stmt).all()


@router.patch("/{vid}", response_model=VideoOut)
async def patch_video(
    vid: str,
    title: str = Form(""),
    description: str = Form(""),
    status: Optional[VideoStatus] = Form(None, description="Active | Archived"),
    session: Session = Depends(get_session),
    _=Depends(admin_guard),
):
    item = ensure_exists(session, vid)

    if title.strip() != "":
        item.title = title
    if description.strip() != "":
        item.description = description
    if status is not None:
        item.status = status

    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/{vid}/replace-file", response_model=VideoOut)
async def replace_video_file(
    vid: str,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _=Depends(admin_guard),
):
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "file must be a video/*")

    item = ensure_exists(session, vid)
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    new_obj_key = f"videos/{vid}/source{ext}"
    old_key = item.video

    upload_obj(file.file, new_obj_key, guess_ct(file.filename, file.content_type))

    # удалить старый, если отличается
    try:
        if old_key and old_key != new_obj_key:
            s3.delete_object(Bucket=S3_BUCKET, Key=old_key)
    except Exception:
        pass

    # (опционально) метаданные нового объекта
    try:
        head = s3.head_object(Bucket=S3_BUCKET, Key=new_obj_key)
        etag = head.get("ETag", "").strip('"')
        size = head.get("ContentLength")
        print(f"[REPLACED] {vid} -> {new_obj_key} etag={etag} size={size}")
    except Exception:
        pass

    item.video = new_obj_key
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/{vid}/archive", response_model=VideoOut)
def archive_video(vid: str, session: Session = Depends(get_session), _=Depends(admin_guard),):
    item = ensure_exists(session, vid)
    item.status = VideoStatus.ARCHIVED
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/{vid}/restore", response_model=VideoOut)
def restore_video(vid: str, session: Session = Depends(get_session), _=Depends(admin_guard),):
    item = ensure_exists(session, vid)
    item.status = VideoStatus.ACTIVE
    item.updated_at = datetime.utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{vid}", response_model=dict)
def soft_delete_video(vid: str, session: Session = Depends(get_session), _=Depends(admin_guard),):
    item = ensure_exists(session, vid)
    item.deleted_at = datetime.utcnow()
    item.updated_at = item.deleted_at
    session.add(item)
    session.commit()
    return {"deleted": vid}


@router.get("/{vid}/play")
def get_play_links(vid: str, session: Session = Depends(get_session), _=Depends(admin_guard),):
    item = ensure_exists(session, vid)

    # не даём играть архив/удалённые
    if item.deleted_at or item.status == VideoStatus.ARCHIVED:
        raise HTTPException(404, "Video not available")

    # проверка наличия файла
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=item.video)
    except Exception:
        raise HTTPException(410, "Video file missing from storage")  # 410 Gone

    ts = int(datetime.utcnow().timestamp())
    return {
        "video_url": presign_get(item.video, 3600) + f"&_={ts}",
        "preview_url": presign_get(item.preview_img, 3600) + f"&_={ts}",
        "status": item.status,
    }
