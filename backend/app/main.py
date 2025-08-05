from fastapi import FastAPI
from app.database.base import Base, engine
from app.api import videos, search 

# 在应用启动时创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent Video Analysis Platform",
    description="An API for uploading, processing, and searching video content.",
    version="1.0.0"
)

# 包含 API 路由
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(search.router, prefix="/api/search", tags=["Search"]) 

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Video Analysis API"}

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"} 