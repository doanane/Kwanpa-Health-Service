# app/config.py
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Database - Use Azure if provided, otherwise local
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # If no DATABASE_URL is set, use local PostgreSQL
    LOCAL_DB_URL: str = "postgresql+psycopg2://postgres:S%400570263170s@localhost:5432/hewal3_db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "-GHyAbetQfDupfx6XXyDkSu0vVkKzmdG4kIMYp7Q13A")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    CORS_ORIGINS: List[str] = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]'))

settings = Settings()