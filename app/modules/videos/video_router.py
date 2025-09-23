from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel import Session

from app.core.db import get_session
from app.modules.auth.auth_router import admin_guard
from app.modules.videos.video_service import VideoService
from app.utils.utils_media import is_image_stream
from app.modules.videos.video_repository import VideoStatus
from app.schemas import VideoOut

router = APIRouter(prefix="/videos", tags=["videos"])


def svc(session: Session = Depends(get_session)) -> VideoService:
    return VideoService(session)


@router.post("", response_model=VideoOut, dependencies=[Depends(admin_guard)])
async def create_video(
    title: str = Form(...),
    description: str = Form(...),
    preview: UploadFile = File(..., description="preview image"),
    file: UploadFile = File(..., description="video file"),
    service: VideoService = Depends(svc),
):
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "file must be a video/*")
    if not is_image_stream(preview.file, preview.content_type):
        raise HTTPException(400, "preview must be a real image (jpg/png/webp/gif)")

    return service.create(
        title=title,
        description=description,
        preview_file=preview.file,
        preview_name=preview.filename or "preview.jpg",
        preview_ct=preview.content_type,
        video_file=file.file,
        video_name=file.filename or "video.mp4",
        video_ct=file.content_type,
    )


@router.get("", response_model=List[VideoOut], dependencies=[Depends(admin_guard)])
def list_videos(
    status: Optional[VideoStatus] = Query(default=None),
    q: Optional[str] = Query(default=None, description="substring in title/description"),
    limit: int = 50,
    offset: int = 0,
    service: VideoService = Depends(svc),
):
    return service.list(status=status, q=q, limit=limit, offset=offset)


@router.patch("/{vid}", response_model=VideoOut, dependencies=[Depends(admin_guard)])
async def patch_video(
    vid: str,
    title: str = Form(""),
    description: str = Form(""),
    status: Optional[VideoStatus] = Form(None, description="Active | Archived"),
    service: VideoService = Depends(svc),
):
    return service.patch(vid, title=title, description=description, status=status)


@router.post("/{vid}/replace-file", response_model=VideoOut, dependencies=[Depends(admin_guard)])
async def replace_video_file(
    vid: str,
    file: UploadFile = File(...),
    service: VideoService = Depends(svc),
):
    if not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "file must be a video/*")
    return service.replace_file(vid, fileobj=file.file, filename=file.filename or "video.mp4", content_type=file.content_type)


@router.post("/{vid}/archive", response_model=VideoOut, dependencies=[Depends(admin_guard)])
def archive_video(vid: str, service: VideoService = Depends(svc)):
    return service.archive(vid)


@router.post("/{vid}/restore", response_model=VideoOut, dependencies=[Depends(admin_guard)])
def restore_video(vid: str, service: VideoService = Depends(svc)):
    return service.restore(vid)


@router.delete("/{vid}", response_model=dict, dependencies=[Depends(admin_guard)])
def soft_delete_video(vid: str, service: VideoService = Depends(svc)):
    return service.soft_delete(vid)


@router.get("/{vid}/play", dependencies=[Depends(admin_guard)])
def get_play_links(vid: str, service: VideoService = Depends(svc)):
    return service.play_links(vid)
