import tempfile
import uuid
from fastapi import HTTPException, UploadFile

from app.models import User
from app.core.logger import logger
from app.core.config import settings
from app.core.s3 import MinioService
from app.schemas import CreateUser, UpdateUser, UserPublic
from app.modules.user.user_repository import UserRepository
from app.services.face_recognition import InsightFaceService


class UserService():
    def __init__(self):
        self.repo = UserRepository()
        self.minio = MinioService()
        self.faceRecognition = InsightFaceService()

    async def create(self, data: CreateUser, image: UploadFile) -> UserPublic:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(await image.read())

            file_key = f"{uuid.uuid4()}.jpg"
            self.minio.upload_file(file_key, tmp_path, settings.AWS_S3_BUCKET_NAME)

            embedding = self.faceRecognition.get_face_embedding(tmp_path)
            if embedding is None:
                raise HTTPException(status_code=400, detail="No face detected")

            return self.repo.create(
                User(
                    name=data.name,
                    number=data.number,
                    organization_id=data.organization_id,
                    image=file_key,
                    embedding=embedding,
                    qr_code=uuid.uuid4(),
                )
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500, detail="Internal server error")

    def findById(self, id: str, org_id: str) -> UserPublic | None:
        try:
            user = self.repo.findById(id, org_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user.image = f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/{user.image}"
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500)

    def findByEmbedding(self, org_id: str, embedding: list[float]) -> list[UserPublic]:
        try:
            users = self.repo.findByEmbedding(org_id, embedding)
            if not users:
                raise HTTPException(status_code=404, detail="No match found")
            for user in users:
                user.image = f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/{user.image}"
            return users
        except HTTPException:
            raise
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500)

    def findAll(self, org_id: str, skip: int | None = None, limit: int | None = None) -> list[UserPublic]:
        try:
            users = self.repo.findAll(org_id, skip, limit)
            for user in users:
                user.image = f"{settings.AWS_S3_PUBLIC_URL}/{settings.AWS_S3_BUCKET_NAME}/{user.image}"
            return users
        except Exception as e:
            logger.error("error %s", e)
            raise HTTPException(status_code=500)

    def updateById(self, id: str, org_id: str, data: UpdateUser) -> UserPublic:
        try:
            user = self.repo.updateById(id, org_id, data)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500)

    def deleteById(self, id: str, org_id: str) -> UserPublic | None:
        try:
            user = self.repo.deleteById(id, org_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500)

    async def recognizeFace(self, image: UploadFile, org_id: str) -> list[UserPublic]:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(await image.read())

            file_key = f"{uuid.uuid4()}.jpg"
            self.minio.upload_file(file_key, tmp_path, settings.AWS_S3_BUCKET_NAME)

            embedding = self.faceRecognition.get_face_embedding(tmp_path)
            if embedding is None:
                raise HTTPException(status_code=400, detail="No face detected")

            return self.findByEmbedding(org_id, embedding)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500)

    async def findOne(self, qr_code: str, org_id: str) -> UserPublic | None:
        try:
            user = self.repo.findOne(qr_code, org_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error("%s", e)
            raise HTTPException(status_code=500)
