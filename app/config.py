import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://lentadnya:lentadnya@db:5432/lentadnya")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-production")
