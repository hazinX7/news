import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./news.db")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-production")
