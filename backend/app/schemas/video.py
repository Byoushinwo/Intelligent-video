from pydantic import BaseModel
from app.models.video import TaskStatus

class VideoCreateResponse(BaseModel):
    message: str
    video_id: int

class VideoStatusResponse(BaseModel):
    video_id: int
    status: TaskStatus
    filename: str