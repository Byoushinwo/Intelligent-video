import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.models.video import Video, TaskStatus
from app.models.subtitle import Subtitle 
from app.schemas.video import VideoCreateResponse
from app.tasks.worker import process_video

router = APIRouter()
MEDIA_PATH = Path("/media") # 这是 Docker 容器内的路径

@router.post("/upload", response_model=VideoCreateResponse)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename found")

    # 将上传的文件保存到 /media 目录
    filepath = MEDIA_PATH / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 创建数据库记录
    # 注意：在我们的新流程中，status 字段由 Celery Worker 管理，
    # Video 模型中的默认值 'PENDING' 会自动生效。
    video_obj = Video(filename=file.filename, filepath=str(filepath))
    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    
    # 派发异步任务给 Celery
    process_video.delay(video_obj.id)
    
    return {"message": "Video uploaded successfully", "video_id": video_obj.id}


# 获取视频详情的 API 端点
@router.get("/{video_id}", summary="Get video details and subtitles")
def get_video_details(video_id: int, db: Session = Depends(get_db)):
    """
    获取单个视频的详细信息，包括其所有按时间排序的字幕。
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    subtitles = db.query(Subtitle).filter(Subtitle.video_id == video_id).order_by(Subtitle.start_time).all()
    
    return {"video": video, "subtitles": subtitles}