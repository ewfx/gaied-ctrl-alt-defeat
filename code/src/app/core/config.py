import os
from pathlib import Path

from dotenv import load_dotenv

# Get the absolute path of the app directory
APP_DIR = Path(__file__).resolve().parent.parent

# Load .env from app directory
dotenv_path = APP_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    print(APP_DIR)
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "gaied")

settings = Settings()
