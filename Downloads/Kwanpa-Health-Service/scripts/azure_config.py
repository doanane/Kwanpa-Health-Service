# azure_config.py
import os
from app.config import settings

# Override settings for Azure
class AzureSettings:
    # Get Azure environment variables
    DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", settings.SECRET_KEY)
    ALGORITHM = os.getenv("ALGORITHM", settings.ALGORITHM)
    
    # Azure-specific
    AZURE_AI_VISION_ENDPOINT = os.getenv("AZURE_AI_VISION_ENDPOINT", "")
    AZURE_AI_VISION_KEY = os.getenv("AZURE_AI_VISION_KEY", "")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY", "")
    
    # URLs for production
    ENVIRONMENT = "production"
    BASE_URL = os.getenv("BASE_URL", "https://hewal3-api.azurewebsites.net")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "https://kwanpa-health-hub-six.vercel.app")
    
    # CORS
    CORS_ORIGINS = [
        "https://kwanpa-health-hub-six.vercel.app",
        "https://hewal3-api.azurewebsites.net",
        "http://localhost:3000",
<<<<<<< HEAD:back/azure_config.py
        "http://localhost:8081",
        "https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net",
=======
>>>>>>> main:back/scripts/azure_config.py
        "http://localhost:8000"
    ]
    
   
    GOOGLE_REDIRECT_URI = f"{BASE_URL}/auth/google/callback"
