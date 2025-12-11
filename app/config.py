# app/config.py
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    # Add these to your Settings class in app/config.py
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_PREFIX: str = os.getenv("API_PREFIX", "")


    # Database - Use Azure if provided, otherwise local
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # If no DATABASE_URL is set, use local PostgreSQL
    LOCAL_DB_URL: str = "postgresql+psycopg2://postgres:S%400570263170s@localhost:5432/hewal3_db"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "-GHyAbetQfDupfx6XXyDkSu0vVkKzmdG4kIMYp7Q13A")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Email & SMS Services
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@hewal3.com")
    HEWAL3_SUPPORT_EMAIL: str = os.getenv("HEWAL3_SUPPORT_EMAIL", "support@hewal3.com")
    
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # Azure AI Services
    AZURE_AI_VISION_ENDPOINT: str = os.getenv("AZURE_AI_VISION_ENDPOINT", "")
    AZURE_AI_VISION_KEY: str = os.getenv("AZURE_AI_VISION_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    CORS_ORIGINS: List[str] = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]'))

settings = Settings()