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
    duplicate_cache_days: int = Field(default=7, env="DUPLICATE_CACHE_DAYS")
    max_attachment_size_mb: int = Field(default=10)
    
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