from typing import Literal, Optional
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    env_ignore_empty=True,
    extra="ignore"
  )
  API_V1_STR: str = "/api/v1"
  ENVIRONMENT: Literal["local", "staging", "production"] = "local"
  POSTGRES_HOST: str
  POSTGRES_PORT: int = 5432
  POSTGRES_USER: str
  POSTGRES_PASSWORD: str
  POSTGRES_DB: str

  JWT_SECRET: str
  JWT_REFRESH_SECRET: str

  REDIS_HOST: str
  REDIS_PORT: int
  REDIS_PASSWORD: Optional[str] = None

  AWS_REGION: Optional[str]
  AWS_ACCESS_KEY_ID: str
  AWS_S3_BUCKET_NAME: str
  AWS_SECRET_ACCESS_KEY: str
  AWS_S3_ENDPOINT_URL: str
  AWS_S3_PUBLIC_URL: str
  
  LOKI_URL: Optional[str]

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
  
settings = Settings()