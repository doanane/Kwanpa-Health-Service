from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "-GHyAbetQfDupfx6XXyDkSu0vVkKzmdG4kIMYp7Q13A")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    
    CORS_ORIGINS: List[str] = eval(os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]'))
    
    
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@hewal3.com")
    HEWAL3_SUPPORT_EMAIL: str = os.getenv("HEWAL3_SUPPORT_EMAIL", "support@hewal3.com")
    
    
    INFOBIP_API_KEY: str = os.getenv("INFOBIP_API_KEY", "")
    INFOBIP_BASE_URL: str = os.getenv("INFOBIP_BASE_URL", "")
    INFOBIP_SENDER_ID: str = os.getenv("INFOBIP_SENDER_ID", "HEWAL3")
    INFOBIP_SENDER_NUMBER: str = os.getenv("INFOBIP_SENDER_NUMBER", "")
    
    
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    
    
    ALLOWED_ORIGINS: List[str] = eval(os.getenv("ALLOWED_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]'))
    
    
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    
    MIN_PASSWORD_LENGTH: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    REQUIRE_PASSWORD_SPECIAL_CHARS: bool = os.getenv("REQUIRE_PASSWORD_SPECIAL_CHARS", "true").lower() == "true"
    REQUIRE_PASSWORD_UPPERCASE: bool = os.getenv("REQUIRE_PASSWORD_UPPERCASE", "true").lower() == "true"
    
    
    AZURE_AI_VISION_ENDPOINT: str = os.getenv("AZURE_AI_VISION_ENDPOINT", "")
    AZURE_AI_VISION_KEY: str = os.getenv("AZURE_AI_VISION_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    
    
    AZURE_IOT_HUB_CONNECTION_STRING: str = os.getenv("AZURE_IOT_HUB_CONNECTION_STRING", "")
    
    
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER: str = os.getenv("AZURE_STORAGE_CONTAINER", "food-images")
    
    
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    API_PREFIX: str = os.getenv("API_PREFIX", "")
    
    
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "-GHyAbetQfDupfx6XXyDkSu0vVkKzmdG4kIMYp7Q13A"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

settings = Settings()