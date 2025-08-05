import subprocess
from pathlib import Path

# 定义媒体文件的根目录，与 docker-compose.yml 中挂载的路径一致
MEDIA_ROOT = Path("/media")

class VideoProcessingError(Exception):
    """自定义异常，用于视频处理失败时抛出"""
    pass

def extract_audio(video_path: Path) -> Path:
    """
    从视频文件中提取音频。
    :param video_path: 原始视频文件的绝对路径 (在容器内)
    :return: 生成的音频文件的绝对路径
    """
    audio_path = video_path.with_suffix(".wav")
    
    # 构建 FFmpeg 命令
    # -i: 输入文件
    # -vn: video no, 忽略视频流
    # -acodec pcm_s16le -ar 16000 -ac 1: 设置音频编码为 Whisper 推荐的格式
    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-y",
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(audio_path)
    ]
    
    print(f"Running FFmpeg command to extract audio: {' '.join(command)}")
    
    try:
        # 执行命令
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("FFmpeg audio extraction successful.")
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)
        return audio_path
    except subprocess.CalledProcessError as e:
        # 如果 FFmpeg 返回非 0 退出码，说明出错了
        print(f"FFmpeg audio extraction failed. Return code: {e.returncode}")
        print("FFmpeg stderr:", e.stderr)
        raise VideoProcessingError(f"Audio extraction failed: {e.stderr}")

def extract_frames(video_path: Path, interval_seconds: int = 5) -> Path:
    """
    从视频中按固定时间间隔抽帧。
    :param video_path: 原始视频文件的绝对路径
    :param interval_seconds: 抽帧间隔（秒）
    :return: 存放所有帧的文件夹路径
    """
    frames_dir = video_path.parent / video_path.stem  # 用视频文件名(不带后缀)创建一个文件夹
    frames_dir.mkdir(exist_ok=True) # 创建文件夹
    
    # 构建 FFmpeg 命令
    # -vf "fps=1/{interval_seconds}": 设置视频滤镜，fps=1/5 表示每 5 秒输出一帧
    # "frame_%04d.jpg": 输出文件的命名格式，如 frame_0001.jpg, frame_0002.jpg
    command = [
        "ffmpeg",
        "-i", str(video_path),
        "-y",
        "-vf", f"fps=1/{interval_seconds}",
        str(frames_dir / "frame_%04d.jpg")
    ]
    
    print(f"Running FFmpeg command to extract frames: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("FFmpeg frame extraction successful.")
        print("FFmpeg stdout:", result.stdout)
        print("FFmpeg stderr:", result.stderr)
        return frames_dir
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg frame extraction failed. Return code: {e.returncode}")
        print("FFmpeg stderr:", e.stderr)
        raise VideoProcessingError(f"Frame extraction failed: {e.stderr}")