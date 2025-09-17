import uuid
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel

# ── Users (по ТЗ: Bearer, телефон+пароль; роли) ───────────────────────────────
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    fullname: str = Field(min_length=2)
    phone: str = Field(unique=True, index=True)
    password: str = Field()                    # хранить ХЭШ (bcrypt/argon2), не plain
    role: str = Field(default="user")          # "user" | "admin"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)
    deleted_at: datetime | None = Field(default=None, nullable=True)  # для soft-delete
