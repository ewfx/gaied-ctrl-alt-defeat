import os
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Any
import json
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

def get_request_types() -> Dict[str, Any]:
    """
    Load request types from JSON file
    """
    data_path = os.path.join(os.path.dirname(__file__), "data", "request_types.json")
    try:
        with open(data_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading request types: {str(e)}")
        return []

def get_extraction_rules() -> Dict[str, Any]:
    """
    Load extraction rules from JSON file
    """
    rules_path = os.path.join(os.path.dirname(__file__), "data", "extraction_rules.json")
    try:
        with open(rules_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading extraction rules: {str(e)}")
        return {
            "default": {
                "priority_sources": ["email_body", "attachment"],
                "fields": ["amount", "account_number", "transaction_id", "client_name", "deal_name", "date"]
            }
        }