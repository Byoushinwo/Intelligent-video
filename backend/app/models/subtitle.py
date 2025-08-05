from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database.base import Base

class Subtitle(Base):
    __tablename__ = "subtitles"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(String)