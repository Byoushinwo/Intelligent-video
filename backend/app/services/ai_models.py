import whisper
from transformers import CLIPProcessor, CLIPModel
import torch

# 判断是否有可用的 GPU，否则使用 CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"AI Models: Using device '{DEVICE}'")

class AIModels:
    """一个单例类，用于在内存中只加载一次模型"""
    _whisper_model = None
    _clip_model = None
    _clip_processor = None

    @classmethod
    def get_whisper_model(cls):
        if cls._whisper_model is None:
            print("Loading Whisper model...")
            # 可以根据需要选择模型大小: tiny, base, small, medium, large
            cls._whisper_model = whisper.load_model("base", device=DEVICE)
            print("Whisper model loaded.")
        return cls._whisper_model

    @classmethod
    def get_clip_model_and_processor(cls):
        if cls._clip_model is None or cls._clip_processor is None:
            print("Loading CLIP model...")
            model_name = "openai/clip-vit-base-patch32"
            cls._clip_model = CLIPModel.from_pretrained(model_name).to(DEVICE)
            cls._clip_processor = CLIPProcessor.from_pretrained(model_name)
            print("CLIP model loaded.")
        return cls._clip_model, cls._clip_processor

# 在模块加载时就初始化，确保 worker 启动时加载
models_loader = AIModels()