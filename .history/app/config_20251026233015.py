from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - will be set by environment variable
    DATABASE_URL: str
    
    # Security - with default values that can be overridden by .env
    SECRET_KEY: str = "-GHyAbetQfDupfx6XXyDkSu0vVkKzmdG4kIMYp7Q13A"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"  # Default to development
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Makes DATABASE_URL and database_url both work