import enum
from sqlalchemy import Column, Integer, String, Enum as SAEnum, DateTime
from sqlalchemy.sql import func
from app.database.base import Base
from . import subtitle

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    filepath = Column(String)
    status = Column(SAEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())