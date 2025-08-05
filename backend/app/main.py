from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base, engine
from app.api import videos, search

# 在应用启动时创建所有数据表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Intelligent Video Analysis Platform",
    description="An API for uploading, processing, and searching video content.",
    version="1.0.0"
)

# --- 添加 CORS 中间件 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 包含 API 路由 ---
app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])

# --- 挂载静态文件目录 ---
# 这会将容器内的 /media 目录映射到 URL 路径 /media
app.mount("/media", StaticFiles(directory="/media"), name="media")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Video Analysis API"}

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "healthy"}