from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 基础配置
    POSTGRES_URL: str
    REDIS_URL: str

    # ChromaDB 配置
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001

    # Pydantic-settings 会自动读取环境变量并填充这些字段
    class Config:
        case_sensitive = False

settings = Settings()