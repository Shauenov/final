# app/core/config.py
from typing import Literal, Optional
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    # DB
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # JWT
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str

    # Redis (не обязателен)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_PASSWORD: Optional[str] = None

    # S3 / MinIO
    AWS_REGION: Optional[str] = None
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_ENDPOINT_URL: str            # http(s)://host:port
    AWS_S3_BUCKET_NAME: str
    AWS_S3_SECURE: Optional[bool] = None  # если не указан — выводим из схемы URL

    # Логи/метрики (опционально)
    ENABLE_METRICS: bool = False
    ENABLE_LOKI: bool = False
    LOKI_URL: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    # Пул БД (опционально)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

settings = Settings()
