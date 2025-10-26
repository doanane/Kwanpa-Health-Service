from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    
    DATABASE_URL: str
    
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()