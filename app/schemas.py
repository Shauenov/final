import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models import ActivityType

class CreateOrganization(BaseModel):
  name: str = Field(
    min_length=2,
    examples=["Hello"]
  )
  fullname: str = Field(
    min_length=2,
    examples=["Chingizkhan Json"]
  )
  password: str = Field(
    min_length=8,
    examples=["admin123"]
  )
  number: str = Field(
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )

class UpdateOrganization(BaseModel):
  name: Optional[str] = Field(default=None, min_length=2, examples=["New name"])
  fullname: Optional[str] = Field(default=None, min_length=2, examples=["Chingiz Jonson"])
  password: Optional[str] = Field(default=None, min_length=8, examples=["newpassword123"])
  number: Optional[str] = Field(default=None, pattern=r"^\+7\d{10}$", examples=["+77015554433"])

class OrganizationPublic(BaseModel):
  id: uuid.UUID
  name: str = Field(examples=["TANBA TOO"])
  fullname: str = Field(examples=["China Jons"])
  number: str = Field(examples=["+77714458954"])
  users: list["UserPublic"] = []
  devices: list["DevicePublic"] = []
  created_at: datetime

  class Config:
    from_attributes = True

class CreateDevice(BaseModel):
  name: str = Field(examples=["Samsung Galaxy Z Flip 4"])
  external_id: uuid.UUID
  organization_id: uuid.UUID

class UpdateDevice(BaseModel):
    name: Optional[str] = Field(default=None, examples=["New Device Name"])
    external_id: Optional[uuid.UUID] = Field(default=None, examples=[uuid.uuid4()])
  
class DevicePublic(BaseModel):
  id: uuid.UUID
  name: str = Field(examples=["Samsung Galaxy Z Flip 4"])
  external_id: uuid.UUID
  organization_id: uuid.UUID
  created_at: datetime

  class Config:
      from_attributes = True

class CreateUser(BaseModel):
  name: str = Field(
    min_length=2,
    examples=["Chingizkhan Johnson"]
  )
  number: str = Field(
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )
  organization_id: uuid.UUID


class UpdateUser(BaseModel):
  name: Optional[str] = Field(
    default=None, 
    min_length=2,
    examples=["Chingizkhan Johnson"]
  )
  number: Optional[str] = Field(
    default=None,
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )
  at_work: Optional[bool] = Field(default=None)

class UserPublic(BaseModel):
  id: uuid.UUID
  name: str = Field(examples=["Chingizkhan Johnson"])
  image: str
  number: str = Field(examples=["+77714458954"])
  at_work: bool = Field(examples=[True])
  qr_code: str = Field(examples=[uuid.uuid4()])
  
  class Config:
    from_attributes = True

class CreateUserAction(BaseModel):
  at_work: bool = Field(examples=[True])
  
  class Config:
    from_attributes = True

class CreateReport(BaseModel):
  name: str = Field(
    min_length=2,
    examples=["Chingizkhan Johnson"]
  )
  number: str = Field(
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )
  organization_id: uuid.UUID


class UpdateReport(BaseModel):
  name: Optional[str] = Field(
    default=None, 
    min_length=2,
    examples=["Chingizkhan Johnson"]
  )
  number: Optional[str] = Field(
    default=None,
    pattern=r"^\+7\d{10}$",
    examples=["+77474156800"]
  )

class ReportPublic(BaseModel):
  id: uuid.UUID
  name: str = Field(examples=["Chingizkhan Johnson"])
  number: str = Field(examples=["+77714458954"])

  class Config:
    from_attributes = True

class CreateUserActivity(BaseModel):
  user_id: uuid.UUID
  type: ActivityType

class UserActivityPublic(BaseModel):
  id: uuid.UUID
  user: UserPublic
  type: ActivityType
  created_at: datetime
  
  class Config:
    from_attributes = True


