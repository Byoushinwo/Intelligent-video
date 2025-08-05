from celery import Celery, states
from celery.exceptions import Ignore
from asgiref.sync import async_to_sync
from app.core.config import settings
from app.database.base import SessionLocal
from app.models.video import Video, TaskStatus
from app.models.subtitle import Subtitle
from app.services.video_processing import ( #导入新函数
    extract_audio,
    extract_frames,
    extract_specific_frame, 
    VideoProcessingError
)
from app.services.ai_models import models_loader, DEVICE
from app.services.vector_db_service import vector_db_service
from app.services.search_engine_service import search_engine_service
from pathlib import Path
from PIL import Image
import torch

# 初始化 Celery 应用
celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.task_routes = {"app.tasks.worker.*": "main-queue"}


# 索引任务
@celery_app.task(name="index_subtitles")
def index_subtitles_task(subtitles: list[dict]):
    """
    一个异步任务，用于将字幕索引到 Elasticsearch 中。
    """
    print(f"收到索引 {len(subtitles)} 条字幕的任务。")
    @async_to_sync
    async def main():
        await search_engine_service.create_index_if_not_exists()
        await search_engine_service.index_subtitles(subtitles)
    try:
        main()
        print("字幕成功索引。")
    except Exception as e:
        print(f"索引字幕时发生错误: {e}")


@celery_app.task(bind=True, name="process_video", max_retries=3)
def process_video(self, video_id: int):
    """
    Celery 任务：完整处理单个视频文件。
    """
    db = SessionLocal()
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        print(f"Video with id {video_id} not found in database. Ignoring task.")
        raise Ignore()

    print(f"Starting full processing pipeline for video_id: {video.id}")

    try:
        video.status = TaskStatus.PROCESSING
        db.commit()

        video_path = Path(video.filepath)
        audio_path = extract_audio(video_path)
        frames_dir = extract_frames(video_path, interval_seconds=5)
        print(f"Media pre-processing successful. Audio: {audio_path}, Frames dir: {frames_dir}")

        whisper_model = models_loader.get_whisper_model()
        transcription_result = whisper_model.transcribe(str(audio_path), fp16=torch.cuda.is_available())

        subtitles_to_add = []
        for segment in transcription_result["segments"]:
            new_subtitle = Subtitle(
                video_id=video_id, start_time=segment["start"],
                end_time=segment["end"], text=segment["text"]
            )
            subtitles_to_add.append(new_subtitle)
        
        db.add_all(subtitles_to_add)
        db.commit()
        print(f"Subtitles for video {video_id} saved to database.")

        subtitles_for_es = [
            {"id": sub.id, "video_id": sub.video_id, "start_time": sub.start_time, "text": sub.text}
            for sub in subtitles_to_add
        ]
        index_subtitles_task.delay(subtitles_for_es)

        clip_model, clip_processor = models_loader.get_clip_model_and_processor()
        embeddings_batch, metadatas_batch, ids_batch = [], [], []
        frame_files = sorted(list(frames_dir.glob("*.jpg")))
        for frame_path in frame_files:
            try:
                image = Image.open(frame_path)
                inputs = clip_processor(images=image, return_tensors="pt").to(DEVICE)
                with torch.no_grad():
                    image_features = clip_model.get_image_features(**inputs)
                
                embeddings_batch.append(image_features[0].cpu().numpy().tolist())
                metadatas_batch.append({
                    "video_id": video_id, "video_filename": video.filename,
                    "frame_filename": frame_path.name,
                    "timestamp_approx": int(frame_path.stem.split("_")[-1]) * 5
                })
                ids_batch.append(f"video_{video_id}_frame_{frame_path.stem}")
            except Exception as frame_exc:
                print(f"Could not process frame {frame_path}: {frame_exc}")
                continue

        vector_db_service.add_embeddings(embeddings_batch, metadatas_batch, ids_batch)
        print(f"Frame embeddings for video {video_id} saved to vector database.")
        
        # --- 新增生成封面的步骤 ---
        print(f"Generating cover frame for video {video_id}...")
        extract_specific_frame(video_path, frame_time=1.0) # 提取第1秒的画面作为封面

        # --- 最终状态更新 ---
        video.status = TaskStatus.COMPLETED
        db.commit()
        return {"status": "Completed"}

    except Exception as e:
        print(f"Task for video {video_id} failed with error: {e}")
        db.rollback()
        video_to_fail = db.query(Video).filter(Video.id == video_id).first()
        if video_to_fail:
            video_to_fail.status = TaskStatus.FAILED
            db.commit()
        
        self.update_state(state=states.FAILURE, meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise Ignore()

    finally:
        db.close()