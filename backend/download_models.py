import os

# 确保使用国内镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['HF_HOME'] = '/root/.cache/huggingface'

import whisper
from transformers import CLIPProcessor, CLIPModel
from sentence_transformers import SentenceTransformer

def download_all_models():
    print("--- Downloading Whisper model (base) ---")
    try:
        whisper.load_model("base")
        print("Whisper model downloaded successfully.")
    except Exception as e:
        print(f"Failed to download Whisper model: {e}")

    print("\n--- Downloading CLIP model (openai/clip-vit-base-patch32) ---")
    try:
        model_name = "openai/clip-vit-base-patch32"
        CLIPModel.from_pretrained(model_name)
        CLIPProcessor.from_pretrained(model_name)
        print("CLIP model and processor downloaded successfully.")
    except Exception as e:
        print(f"Failed to download CLIP model: {e}")
        
    # 下载 ChromaDB 依赖的 embedding model
    print("\n--- Downloading ChromaDB embedding model (all-MiniLM-L6-v2) ---")
    try:
        model_name = "all-MiniLM-L6-v2"
        SentenceTransformer(model_name)
        print("ChromaDB embedding model downloaded successfully.")
    except Exception as e:
        print(f"Failed to download ChromaDB embedding model: {e}")

if __name__ == "__main__":
    download_all_models()
