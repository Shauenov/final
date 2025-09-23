
from datetime import datetime
import uuid
from pydantic import BaseModel


class StatisticsBase(BaseModel):
  device_id: uuid.UUID
  content_id: uuid.UUID
  watched_full: bool = False

class StatisticsCreate(StatisticsBase):
  pass

class StatisticsPublic(StatisticsBase):
  id: uuid.UUID
  created_at: datetime

  class Config:
      from_attributes = True