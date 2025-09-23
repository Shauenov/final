from __future__ import annotations

import os
import uuid
import tempfile
import mimetypes
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlmodel import Session

from app.core.config import settings
from app.core.s3 import MinioService
from app.models import Book
from app.schemas import BookCreate, BookUpdate
from app.modules.books.book_repository import BookRepository

ALLOWED_BOOK_MIMES = {
    "application/pdf",
    "application/epub+zip",
}
ALLOWED_COVER_PREFIX = "image/"


def _bucket() -> str:
    return getattr(settings, "AWS_S3_BUCKET_NAME", None) or os.getenv("S3_BUCKET") or "bus_storage"


def _guess_ct(name: str, fallback: str = "application/octet-stream") -> str:
    ctype, _ = mimetypes.guess_type(name or "")
    return ctype or fallback


def _upload_file(minio: MinioService, bucket: str, object_name: str, file: UploadFile) -> str:
    """
    Пишем UploadFile во временный файл и используем MinioService.upload_file.
    Возвращает публичный URL (как реализовано в MinioService).
    """
    file.file.seek(0)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    try:
        return minio.upload_file(object_name, tmp_path, bucket, content_type=_guess_ct(file.filename))
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


class BookService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = BookRepository(session)
        self.minio = MinioService()
        self.bucket = _bucket()

    def _ensure(self, book_id: uuid.UUID) -> Book:
        book = self.repo.get(book_id)
        if not book or book.deleted_at:
            raise HTTPException(404, "Book not found")
        return book

    # CREATE
    def create(
        self,
        *,
        created_by: uuid.UUID,
        body: BookCreate,
        file: UploadFile,
        cover: Optional[UploadFile],
    ) -> Book:
        # validate file
        if (file.content_type or "").lower() not in ALLOWED_BOOK_MIMES:
            raise HTTPException(400, "file must be PDF or EPUB")

        # validate cover (если передали)
        if cover and not (cover.content_type or "").lower().startswith(ALLOWED_COVER_PREFIX):
            raise HTTPException(400, "cover must be an image/*")

        new_id = uuid.uuid4()

        # файл книги
        file_ext = os.path.splitext(file.filename or "")[1]
        if not file_ext:
            file_ext = ".pdf" if (file.content_type or "").lower() == "application/pdf" else ".epub"
        file_key = f"books/{new_id}/file{file_ext}"
        file_url = _upload_file(self.minio, self.bucket, file_key, file)

        # обложка (если есть)
        cover_url = None
        if cover:
            cover_ext = os.path.splitext(cover.filename or "")[1] or ".jpg"
            cover_key = f"books/{new_id}/cover{cover_ext}"
            cover_url = _upload_file(self.minio, self.bucket, cover_key, cover)

        book = Book(
            id=new_id,
            title=body.title,
            author=body.author,
            description=body.description,
            genre=body.genre,
            published_year=body.published_year,
            file_url=file_url,
            cover_url=cover_url,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        return self.repo.create(book)

    # READ
    def list(self, *, q: Optional[str], genre: Optional[str], author: Optional[str], year: Optional[int], limit: int, offset: int):
        return self.repo.list(q=q, genre=genre, author=author, year=year, limit=limit, offset=offset)

    def get(self, book_id: uuid.UUID) -> Book:
        return self._ensure(book_id)

    # UPDATE (метаданные JSON)
    def update_meta(self, book_id: uuid.UUID, patch: BookUpdate) -> Book:
        book = self._ensure(book_id)
        data = patch.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(book, k, v)
        return self.repo.save(book)

    # REPLACE FILES
    def replace_file(self, book_id: uuid.UUID, file: UploadFile) -> Book:
        if (file.content_type or "").lower() not in ALLOWED_BOOK_MIMES:
            raise HTTPException(400, "file must be PDF or EPUB")

        book = self._ensure(book_id)
        ext = os.path.splitext(file.filename or "")[1]
        if not ext:
            ext = ".pdf" if (file.content_type or "").lower() == "application/pdf" else ".epub"
        key = f"books/{book_id}/file{ext}"

        file_url = _upload_file(self.minio, self.bucket, key, file)
        book.file_url = file_url
        return self.repo.save(book)

    def replace_cover(self, book_id: uuid.UUID, cover: UploadFile) -> Book:
        if not (cover.content_type or "").lower().startswith(ALLOWED_COVER_PREFIX):
            raise HTTPException(400, "cover must be an image/*")

        book = self._ensure(book_id)
        ext = os.path.splitext(cover.filename or "")[1] or ".jpg"
        key = f"books/{book_id}/cover{ext}"

        cover_url = _upload_file(self.minio, self.bucket, key, cover)
        book.cover_url = cover_url
        return self.repo.save(book)

    # SOFT DELETE
    def soft_delete(self, book_id: uuid.UUID) -> dict:
        book = self._ensure(book_id)
        book.deleted_at = datetime.utcnow()
        self.repo.save(book)
        return {"deleted": str(book_id)}
