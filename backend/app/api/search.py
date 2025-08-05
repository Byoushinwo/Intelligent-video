from fastapi import APIRouter, Query
from app.services.search_engine_service import search_engine_service
from app.services.vector_db_service import vector_db_service
from app.services.ai_models import models_loader, DEVICE
import torch

router = APIRouter()

@router.get("/text", summary="Search subtitles by text")
async def search_by_text(q: str = Query(..., min_length=1, description="Search query for subtitles")):
    """
    根据关键词在所有视频的字幕中进行全文检索。
    """
    results = await search_engine_service.search_subtitles_by_text(query_text=q)
    return {"query": q, "results": results}

@router.get("/image-by-text", summary="Search images by text description")
def search_image_by_text(q: str = Query(..., min_length=1, description="Textual description of an image to search for")):
    """
    以文搜图：使用文本描述在所有视频帧中检索最相似的图像。
    """
    # 1. 加载 CLIP 模型
    clip_model, clip_processor = models_loader.get_clip_model_and_processor()
    
    # 2. 将查询文本编码为向量
    inputs = clip_processor(text=[q], return_tensors="pt", padding=True).to(DEVICE)
    with torch.no_grad():
        text_features = clip_model.get_text_features(**inputs)
    query_vector = text_features[0].cpu().numpy().tolist()
    
    # 3. 在 ChromaDB 中进行向量相似度查询
    query_results = vector_db_service.collection.query(
        query_embeddings=[query_vector],
        n_results=10 # 返回最相似的 10 个结果
    )
    return {"query": q, "results": query_results}