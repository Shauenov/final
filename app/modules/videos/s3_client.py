# app/modules/videos/s3_client.py
import os, boto3
from botocore.config import Config
from boto3.s3.transfer import TransferConfig
from urllib.parse import urlparse, urlunparse

S3_ENDPOINT = os.getenv("S3_ENDPOINT") or os.getenv("AWS_S3_ENDPOINT_URL")
S3_PUBLIC_URL = os.getenv("S3_PUBLIC_URL")  # <-- добавили
S3_REGION   = os.getenv("S3_REGION", "us-east-1")
S3_KEY      = os.getenv("S3_ACCESS_KEY") or os.getenv("AWS_ACCESS_KEY_ID")
S3_SECRET   = os.getenv("S3_SECRET_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET   = os.getenv("S3_BUCKET") or os.getenv("AWS_S3_BUCKET_NAME")

session = boto3.session.Session()
s3 = session.client(
    "s3",
    region_name=S3_REGION,
    endpoint_url=S3_ENDPOINT,                    # внутренний адрес для SDK
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    config=Config(s3={"addressing_style": "path"})
)

MB = 1024**2
transfer_cfg = TransferConfig(multipart_threshold=8*MB, multipart_chunksize=8*MB)

def guess_ct(name: str, fallback="application/octet-stream"):
    import mimetypes
    return mimetypes.guess_type(name)[0] or fallback

def upload_obj(fileobj, key: str, content_type: str):
    s3.upload_fileobj(
        Fileobj=fileobj,
        Bucket=S3_BUCKET,
        Key=key,
        ExtraArgs={"ContentType": content_type},
        Config=transfer_cfg
    )
    return key

def presign_get(key: str, expires=3600) -> str:
    url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=expires
    )
    # Переписываем хост/схему на публичные (для браузера)
    if S3_PUBLIC_URL:
        u = urlparse(url)
        p = urlparse(S3_PUBLIC_URL)
        url = urlunparse((
            p.scheme or u.scheme,
            p.netloc or u.netloc,
            u.path, u.params, u.query, u.fragment
        ))
    return url
