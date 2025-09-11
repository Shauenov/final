import enum
import uuid
from datetime import datetime, UTC
from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel
from sqlalchemy.types import Enum as SQLAlchemyEnum

class Organization(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  name: str = Field(min_length=2, unique=True)
  fullname: str = Field(min_length=2)
  password: str = Field()
  number: str = Field(unique=True)
  users: list["User"] = Relationship(back_populates="organization", cascade_delete=True)
  devices: list["Device"] = Relationship(back_populates="organization", cascade_delete=True)
  reports: list["Report"] = Relationship(back_populates="organization", cascade_delete=True)
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)

class Device(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  name: str = Field(min_length=2)
  external_id: str = Field()
  organization_id: uuid.UUID = Field(
    foreign_key="organization.id", nullable=False, ondelete="CASCADE"
  )
  organization: Organization | None = Relationship(
    back_populates="devices"
  )
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)

class User(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  organization_id: uuid.UUID = Field(
    foreign_key="organization.id", nullable=False, ondelete="CASCADE"
  )
  organization: Organization | None = Relationship(
    back_populates="users"
  )
  at_work: bool = Field(default=False)
  name: str = Field(min_length=2)
  image: str = Field()
  qr_code: str = Field(unique=True)
  number: str = Field()
  embedding: list[float] = Field(sa_type=Vector(512))
  activity: list["UserActivity"] = Relationship(back_populates="user", cascade_delete=True)
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)

class ActivityType(enum.Enum):
  ENTRY="entry"
  EXIT="exit"

class UserActivity(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  user_id: uuid.UUID = Field(
    foreign_key="user.id", nullable=False, ondelete="CASCADE"
  )
  user: User | None = Relationship(
    back_populates="activity"
  )
  type: ActivityType = Field(
      sa_column=Column(SQLAlchemyEnum(ActivityType, name="activity_type_enum"))
  )
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)


class Report(SQLModel, table=True):
  id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
  organization_id: uuid.UUID = Field(
    foreign_key="organization.id", nullable=False, ondelete="CASCADE"
  )
  organization: Organization | None = Relationship(
    back_populates="reports"
  )
  report_date: datetime
  created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
  updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=True)
