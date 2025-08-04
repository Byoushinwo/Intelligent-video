from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_routes = {"app.tasks.worker.*": "main-queue"}

@celery_app.task(name="process_video")
def process_video(video_id: int):
    # 这是一个占位任务，现在只打印日志
    # 后面所有复杂的逻辑都在这里添加
    print(f"Celery Worker: Received video processing task for video_id: {video_id}")
    # 在真实场景中，你会在这里更新数据库状态、调用 FFmpeg 等
    return {"status": "success", "video_id": video_id}