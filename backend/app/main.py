from fastapi import FastAPI
from app.database.base import Base, engine
from app.api import videos

# 在应用启动时创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Video Analysis Platform")

app.include_router(videos.router, prefix="/api/videos", tags=["Videos"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Analysis API"}