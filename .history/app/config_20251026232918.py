from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - will be set by environment variable
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"

settings = Settings()