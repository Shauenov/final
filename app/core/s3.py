import json
from typing import Optional
from minio import Minio
from minio.error import S3Error
from app.core.logger import logger
from app.core.config import settings

class MinioService:
    def __init__(self):
        # если endpoint начинается с https:// — включим secure=True
        endpoint = settings.AWS_S3_ENDPOINT_URL.replace("https://", "").replace("http://", "")
        secure = settings.AWS_S3_ENDPOINT_URL.startswith("https://") or getattr(settings, "AWS_S3_SECURE", False)

        self.client = Minio(
            endpoint=endpoint,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            region=getattr(settings, "AWS_REGION", None),
            secure=secure,
        )

    def ensure_bucket(self, bucket: str, public_read: bool = False) -> None:
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                if public_read:
                    policy = {
                        "Version": "2012-10-17",
                        "Statement": [{
                            "Action": ["s3:GetObject"],
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Resource": [f"arn:aws:s3:::{bucket}/*"],
                        }],
                    }
                    self.client.set_bucket_policy(bucket, json.dumps(policy))
        except S3Error as e:
            logger.error("ensure_bucket error: %s", e)
            raise

    def upload_file(self, object_name: str, src_path: str, bucket: str, content_type: Optional[str] = None) -> str:
        """Загружает локальный файл в MinIO. Возвращает ключ вида '{bucket}/{object_name}'."""
        try:
            self.ensure_bucket(bucket, public_read=False)
            self.client.fput_object(
                bucket_name=bucket,
                object_name=object_name,
                file_path=src_path,
                content_type=content_type,
            )
            logger.info("uploaded %s to s3://%s/%s", src_path, bucket, object_name)
            return f"{settings.AWS_S3_PUBLIC_URL}/{bucket}/{object_name}"
        except S3Error as e:
            logger.error("upload_file error: %s", e)
            raise

    def delete_object(self, object_name: str, bucket: str) -> None:
        try:
            self.client.remove_object(bucket, object_name)
        except S3Error as e:
            logger.error("delete_object error: %s", e)
            raise

    def presign_get(self, object_name: str, bucket: str, expires_seconds: int = 3600) -> str:
        """Выдаёт временную ссылку на скачивание (рекомендуется вместо public-policy)."""
        try:
            return self.client.presigned_get_object(bucket, object_name, expires=expires_seconds)
        except S3Error as e:
            logger.error("presign_get error: %s", e)
            raise
