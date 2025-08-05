import asyncio 
from celery import Celery, states
from celery.exceptions import Ignore
from app.core.config import settings
from app.database.base import SessionLocal
from app.models.video import Video, TaskStatus
from app.models.subtitle import Subtitle
from app.services.video_processing import extract_audio, extract_frames, VideoProcessingError
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
    async def main():
        await search_engine_service.create_index_if_not_exists()
        await search_engine_service.index_subtitles(subtitles)
    asyncio.run(main())
    print("字幕成功索引。")


@celery_app.task(bind=True, name="process_video", max_retries=3)
def process_video(self, video_id: int):
    """
    Celery 任务：完整处理单个视频文件。
    1. 更新状态为 PROCESSING
    2. [阶段二] 提取音频和视频帧
    3. [阶段三] 进行 AI 分析 (语音转文字、图像向量化)
    4. [阶段四] 将字幕数据异步索引到 Elasticsearch
    5. 更新状态为 COMPLETED 或 FAILED
    """
    db = SessionLocal()
    video = db.query(Video).filter(Video.id == video_id).first()

    if not video:
        print(f"Video with id {video_id} not found in database. Ignoring task.")
        raise Ignore()

    print(f"Starting full processing pipeline for video_id: {video.id}, filepath: {video.filepath}")

    try:
        # --- 状态机流转：PENDING -> PROCESSING ---
        video.status = TaskStatus.PROCESSING
        db.commit()

        video_path = Path(video.filepath)

        # === 阶段二：媒体预处理 ===
        print(f"Step 2: Pre-processing media for video {video.id}...")
        audio_path = extract_audio(video_path)
        frames_dir = extract_frames(video_path, interval_seconds=5)
        print(f"Media pre-processing successful. Audio: {audio_path}, Frames dir: {frames_dir}")

        # === 阶段三：AI 分析 ===

        # --- 3.1 语音转文字 (Whisper) ---
        print(f"Step 3.1: Transcribing audio for video {video.id}...")
        whisper_model = models_loader.get_whisper_model()
        transcription_result = whisper_model.transcribe(str(audio_path), fp16=False)

        subtitles_to_add = []
        for segment in transcription_result["segments"]:
            new_subtitle = Subtitle(
                video_id=video_id,
                start_time=segment["start"],
                end_time=segment["end"],
                text=segment["text"]
            )
            subtitles_to_add.append(new_subtitle)
        
        db.add_all(subtitles_to_add)
        db.commit()
        print(f"Subtitles for video {video.id} saved to database.")

        # 新增派发索引任务的步骤
        print(f"派发索引任务给 Elasticsearch...")
        subtitles_for_es = [
            {"id": sub.id, "video_id": sub.video_id, "start_time": sub.start_time, "text": sub.text}
            for sub in subtitles_to_add
        ]
        index_subtitles_task.delay(subtitles_for_es)


        # --- 3.2 图像向量化 (CLIP) ---
        print(f"Step 3.2: Embedding frames for video {video.id}...")
        clip_model, clip_processor = models_loader.get_clip_model_and_processor()
        
        embeddings_batch = []
        metadatas_batch = []
        ids_batch = []

        frame_files = sorted(list(frames_dir.glob("*.jpg")))
        for frame_path in frame_files:
            try:
                image = Image.open(frame_path)
                inputs = clip_processor(images=image, return_tensors="pt").to(DEVICE)
                
                with torch.no_grad():
                    image_features = clip_model.get_image_features(**inputs)
                
                embeddings_batch.append(image_features[0].cpu().numpy().tolist())
                metadatas_batch.append({
                    "video_id": video_id,
                    "frame_filename": frame_path.name,
                    "timestamp_approx": int(frame_path.stem.split("_")[-1]) * 5
                })
                ids_batch.append(f"video_{video_id}_frame_{frame_path.stem}")
            except Exception as frame_exc:
                print(f"Could not process frame {frame_path}: {frame_exc}")
                continue

        vector_db_service.add_embeddings(embeddings_batch, metadatas_batch, ids_batch)
        print(f"Frame embeddings for video {video.id} saved to vector database.")

        # --- 状态机流转：PROCESSING -> COMPLETED ---
        print(f"Processing pipeline completed for video {video.id}.")
        video.status = TaskStatus.COMPLETED
        db.commit()

        return {"status": "Completed"}

    except VideoProcessingError as e:
        print(f"A processing error occurred for video {video.id}: {e}")
        video.status = TaskStatus.FAILED
        db.commit()
        self.update_state(state=states.FAILURE, meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise Ignore()

    except Exception as e:
        print(f"An unexpected error occurred for video {video.id}: {e}")
        video.status = TaskStatus.FAILED
        db.commit()
        try:
            print(f"Retrying task in 60 seconds... (Attempt {self.request.retries + 1} of {self.max_retries})")
            raise self.retry(exc=e, countdown=60)
        except self.MaxRetriesExceededError:
            print(f"Task for video {video.id} failed after max retries.")
            self.update_state(state=states.FAILURE, meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
            raise Ignore()

    finally:
        db.close()