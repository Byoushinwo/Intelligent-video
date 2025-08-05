import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings

class VectorDBService:
    def __init__(self):
        # 连接到 Docker 中的 ChromaDB 服务
        self.client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        # 使用 CLIP 模型作为默认的 embedding function (虽然我们自己算向量，但 collection 需要一个)
        clip_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="clip-ViT-B-32")
        self.collection = self.client.get_or_create_collection(
            name="video_frames",
            embedding_function=clip_ef # 只是为了满足 API 要求
        )

    def add_embeddings(self, embeddings: list, metadatas: list, ids: list):
        """批量添加向量和元数据到 ChromaDB"""
        if not ids:
            return
        print(f"Adding {len(ids)} embeddings to ChromaDB...")
        self.collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print("Embeddings added successfully.")

vector_db_service = VectorDBService()