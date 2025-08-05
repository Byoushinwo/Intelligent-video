import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder # 从 fastapi.encoders 导入
from sqlalchemy.orm import Session
from sqlalchemy import desc 
from app.database.base import get_db
from app.models.video import Video
from app.models.subtitle import Subtitle 
from app.schemas.video import VideoCreateResponse
from app.tasks.worker import process_video

router = APIRouter()
MEDIA_PATH = Path("/media")
API_BASE_URL = "http://127.0.0.1:8000" # 用于构建封面URL

@router.get("/", summary="Get a list of all videos")
def get_video_list(db: Session = Depends(get_db)):
    """
    获取所有视频的列表，按上传时间倒序排列，并为每个视频添加封面URL。
    """
    videos = db.query(Video).order_by(desc(Video.created_at)).all()
    
    # 将 SQLAlchemy 对象转换为可修改的字典
    videos_data = jsonable_encoder(videos)
    
    # 动态添加 cover_url 字段
    for video_dict in videos_data:
        filename_without_ext = Path(video_dict.get('filename', '')).stem
        if filename_without_ext:
            video_dict['cover_url'] = f"{API_BASE_URL}/media/{filename_without_ext}/cover.jpg"
        else:
            video_dict['cover_url'] = None # 处理异常情况
            
    return videos_data

@router.post("/upload", response_model=VideoCreateResponse)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename found")

    filepath = MEDIA_PATH / file.filename
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    video_obj = Video(filename=file.filename, filepath=str(filepath))
    db.add(video_obj)
    db.commit()
    db.refresh(video_obj)
    
    process_video.delay(video_obj.id)
    
    return {"message": "Video uploaded successfully", "video_id": video_obj.id}

@router.get("/{video_id}", summary="Get video details and subtitles")
def get_video_details(video_id: int, db: Session = Depends(get_db)):
    """
    获取单个视频的详细信息，包括其所有字幕和封面URL。
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    subtitles = db.query(Subtitle).filter(Subtitle.video_id == video_id).order_by(Subtitle.start_time).all()
    
    video_data = jsonable_encoder(video)
    filename_without_ext = Path(video_data.get('filename', '')).stem
    if filename_without_ext:
        video_data['cover_url'] = f"{API_BASE_URL}/media/{filename_without_ext}/cover.jpg"
    else:
        video_data['cover_url'] = None
        
    return {"video": video_data, "subtitles": subtitles}