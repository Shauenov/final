# migrate_keys.py
import os, re
from sqlmodel import Session, select, create_engine
from models import Video
from s3_client import s3, presign_get

BUCKET = os.getenv("S3_BUCKET")

engine = create_engine("sqlite:///./app.db")
pat = re.compile(r"^videos/[0-9a-f-]{36}/source\.[a-z0-9]+$", re.I)

with Session(engine) as s:
    videos = s.exec(select(Video).where(Video.deleted_at.is_(None))).all()
    for v in videos:
        old = v.video
        if old and not pat.match(old):
            ext = os.path.splitext(old)[1] or ".mp4"
            new = f"videos/{v.id}/source{ext}"

            # копия в новый ключ
            s3.copy_object(
                Bucket=BUCKET,
                CopySource={"Bucket": BUCKET, "Key": old},
                Key=new
            )
            # удалить старый
            s3.delete_object(Bucket=BUCKET, Key=old)

            v.video = new
            s.add(v)
    s.commit()
print("Migration done.")
