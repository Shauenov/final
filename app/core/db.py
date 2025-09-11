from typing import Generator
from sqlmodel import Session, create_engine, SQLModel

from app.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URL))

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)