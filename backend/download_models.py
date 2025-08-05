# backend/download_models.py
import os

# 设置环境变量，确保下载到国内镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = '/root/.cache/huggingface'

import whisper
from transformers import CLIPProcessor, CLIPModel

def download_all_models():
    """
    下载并缓存本项目所需的所有 AI 模型。
    """
    print("--- Downloading Whisper model ---")
    try:
        whisper.load_model("base")
        print("Whisper model downloaded successfully.")
    except Exception as e:
        print(f"Failed to download Whisper model: {e}")

    print("\n--- Downloading CLIP model ---")
    try:
        model_name = "openai/clip-vit-base-patch32"
        CLIPModel.from_pretrained(model_name)
        CLIPProcessor.from_pretrained(model_name)
        print("CLIP model and processor downloaded successfully.")
    except Exception as e:
        print(f"Failed to download CLIP model: {e}")

if __name__ == "__main__":
    download_all_models()