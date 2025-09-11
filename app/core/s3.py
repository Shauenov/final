import json
from minio import Minio
from minio.error import S3Error
from app.core.logger import logger
from app.core.config import settings

class MinioService:
  def __init__(self):
    self.client = Minio(
      endpoint=settings.AWS_S3_ENDPOINT_URL,
      access_key=settings.AWS_ACCESS_KEY_ID,
      secret_key=settings.AWS_SECRET_ACCESS_KEY,
      region=settings.AWS_REGION,
      secure=False
    )

  def create_bucket(self, bucket: str):
    try:
      found = self.client.bucket_exists(bucket)
      if not found:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["s3:GetObject"],
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Resource": [f"arn:aws:s3:::{bucket}/*"],
                }
            ],
        }
        self.client.make_bucket(bucket)
        self.client.set_bucket_policy(bucket, json.dumps(policy))
    except S3Error as e:
      logger.error(e)
      raise e

  def upload_file(self, file_name: str, dest_file_name: bytes, bucket: str) -> str:
    try:
      self.create_bucket(bucket)
    
      self.client.fput_object(
        bucket,
        file_name,
        dest_file_name,
      )

      logger.info("%s successfully uploaded as object %s to bucket %s", file_name, dest_file_name, bucket)
      return f"{bucket}/{file_name}"
    except S3Error as exc:
      logger.error("error occurred.", exc)

  def delete_object(self, object_name, bucket):
    try:
      self.client.remove_object(bucket, object_name)
    except S3Error as e:
      logger.error(e)
      raise e