import chromadb
from app.core.config import settings

class VectorDBService:
    def __init__(self):
        self.client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        
        # 不再指定任何默认的 embedding_function
        # 避免了 ChromaDB 客户端在初始化时去下载任何模型。
        self.collection = self.client.get_or_create_collection(
            name="video_frames"
        )

    def add_embeddings(self, embeddings: list, metadatas: list, ids: list):
        if not ids: return
        self.collection.add(embeddings=embeddings, metadatas=metadatas, ids=ids)

vector_db_service = VectorDBService()
