# app/schemas.py (только блок users)
import uuid
from typing import Optional
from pydantic import BaseModel, Field

PHONE_RE = r"^\+7\d{10}$"

class CreateUser(BaseModel):
    fullname: str = Field(min_length=2)
    phone: str = Field(pattern=PHONE_RE)
    password: str = Field(min_length=8)
    role: Optional[str] = Field(default="user")

class UpdateUser(BaseModel):
    fullname: Optional[str] = Field(default=None, min_length=2)
    phone: Optional[str] = Field(default=None, pattern=PHONE_RE)
    password: Optional[str] = Field(default=None, min_length=8)
    role: Optional[str] = Field(default=None)

class UserPublic(BaseModel):
    id: uuid.UUID
    fullname: str
    phone: str
    role: str
    class Config:
        from_attributes = True
