from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/ragdb"
    
    # Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    
    # OpenAI
    openai_api_key: str
    
    # Application
    debug: bool = True
    log_level: str = "INFO"
    upload_dir: str = "./data/uploads"
    max_file_size: str = "50MB"
    
    # Security
    secret_key: str
    jwt_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"


settings = Settings()