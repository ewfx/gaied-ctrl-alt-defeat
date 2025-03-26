import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Any
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables with defaults
    """
    # Server settings
    port: int = Field(default=8000, env="PORT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Application settings
    duplicate_cache_days: int = Field(default=14, env="DUPLICATE_CACHE_DAYS")
    duplicate_cache_size: int = Field(default=10000, env="DUPLICATE_CACHE_SIZE")
    max_attachment_size_mb: int = Field(default=10, env="MAX_ATTACHMENT_SIZE_MB")
    
    # IntelligentDuplicateDetector settings
    semantic_threshold: float = Field(default=0.85, env="SEMANTIC_THRESHOLD")
    metadata_weight: float = Field(default=0.25, env="METADATA_WEIGHT")
    subject_weight: float = Field(default=0.3, env="SUBJECT_WEIGHT")
    content_weight: float = Field(default=0.9, env="CONTENT_WEIGHT")
    time_window_hours: int = Field(default=72, env="TIME_WINDOW_HOURS")
    
    # Optional settings for embedding provider if using SentenceTransformers
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()