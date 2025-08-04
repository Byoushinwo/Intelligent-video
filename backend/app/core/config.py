from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str
    REDIS_URL: str

settings = Settings()