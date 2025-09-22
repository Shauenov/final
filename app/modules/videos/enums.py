# app/modules/videos/enums.py
from enum import Enum

class VideoStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"
