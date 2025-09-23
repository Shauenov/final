from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import BinaryIO, Optional

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.core.s3 import MinioService
from app.models import Video
from app.modules.videos.video_repository import VideoRepository, VideoStatus


def _guess_ct(name: str, fallback: str = "application/octet-stream") -> str:
    import mimetypes
    return mimetypes.guess_type(name)[0] or fallback


def _bucket() -> str:
    if not getattr(settings, "AWS_S3_BUCKET_NAME", None):
        raise RuntimeError("AWS_S3_BUCKET_NAME is not set")
    return settings.AWS_S3_BUCKET_NAME


def _put_stream(s3: MinioService, bucket: str, key: str, fileobj: BinaryIO, content_type: str):
    # MinIO требует длину потока
    pos = fileobj.tell()
    fileobj.seek(0, 2)
    length = fileobj.tell()
    fileobj.seek(pos, 0)
    if length <= 0:
        from io import BytesIO
        data = fileobj.read()
        length = len(data)
        fileobj = BytesIO(data)

    s3.client.put_object(
        bucket_name=bucket,
        object_name=key,
        data=fileobj,
        length=length,
        content_type=content_type,
    )


class VideoService:
    def __init__(self, session: Session):
        self.repo = VideoRepository(session)
        self.session = session
        self.s3 = MinioService()
        self.bucket = _bucket()

    # --- helpers ---
    def _ensure(self, vid: str) -> Video:
        v = self.repo.get(vid)
        if not v or v.deleted_at:
            raise HTTPException(404, "Video not found")
        return v

    # --- use cases ---
    def create(
        self,
        title: str,
        description: str,
        preview_file,
        preview_name: str,
        preview_ct: Optional[str],
        video_file,
        video_name: str,
        video_ct: Optional[str],
    ) -> Video:
        vid = str(uuid.uuid4())
        preview_ext = os.path.splitext(preview_name)[1] or ".jpg"
        video_ext = os.path.splitext(video_name)[1] or ".mp4"

        preview_key = f"videos/{vid}/preview{preview_ext}"
        video_key = f"videos/{vid}/source{video_ext}"

        _put_stream(self.s3, self.bucket, preview_key, preview_file, _guess_ct(preview_name, preview_ct))
        _put_stream(self.s3, self.bucket, video_key, video_file, _guess_ct(video_name, video_ct))

        v = Video(
            id=vid,
            title=title,
            description=description,
            preview_img=preview_key,
            video=video_key,
            status=VideoStatus.ACTIVE,
        )
        return self.repo.create(v)

    def list(self, status, q, limit: int, offset: int):
        return self.repo.list(status=status, q=q, limit=limit, offset=offset)

    def patch(self, vid: str, *, title: Optional[str], description: Optional[str], status: Optional[VideoStatus]) -> Video:
        v = self._ensure(vid)
        if title and title.strip():
            v.title = title
        if description and description.strip():
            v.description = description
        if status is not None:
            v.status = status
        v.updated_at = datetime.utcnow()
        return self.repo.save(v)

    def replace_file(self, vid: str, *, fileobj, filename: str, content_type: Optional[str]) -> Video:
        v = self._ensure(vid)
        if v.status == VideoStatus.ARCHIVED:
            raise HTTPException(400, "Archived video cannot be modified")

        ext = os.path.splitext(filename)[1] or ".mp4"
        new_key = f"videos/{vid}/source{ext}"
        old_key = v.video

        _put_stream(self.s3, self.bucket, new_key, fileobj, _guess_ct(filename, content_type))
        if old_key and old_key != new_key:
            try:
                self.s3.client.remove_object(self.bucket, old_key)
            except Exception:
                pass

        v.video = new_key
        v.updated_at = datetime.utcnow()
        return self.repo.save(v)

    def archive(self, vid: str) -> Video:
        v = self._ensure(vid)
        v.status = VideoStatus.ARCHIVED
        v.updated_at = datetime.utcnow()
        return self.repo.save(v)

    def restore(self, vid: str) -> Video:
        v = self._ensure(vid)
        v.status = VideoStatus.ACTIVE
        v.updated_at = datetime.utcnow()
        return self.repo.save(v)

    def soft_delete(self, vid: str) -> dict:
        v = self._ensure(vid)
        v.deleted_at = datetime.utcnow()
        v.updated_at = v.deleted_at
        self.repo.save(v)
        return {"deleted": vid}

    def play_links(self, vid: str) -> dict:
        v = self._ensure(vid)
        if v.status == VideoStatus.ARCHIVED:
            raise HTTPException(404, "Video not available")
        try:
            self.s3.client.stat_object(self.bucket, v.video)
        except Exception:
            raise HTTPException(410, "Video file missing from storage")

        ts = int(datetime.utcnow().timestamp())
        return {
            "video_url": self.s3.presign_get(v.video, bucket=self.bucket, expires_seconds=3600) + f"&_={ts}",
            "preview_url": self.s3.presign_get(v.preview_img, bucket=self.bucket, expires_seconds=3600) + f"&_={ts}",
            "status": v.status,
        }
