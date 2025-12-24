# app/config/urls.py
import os
from app.config import settings

# Production URLs
PRODUCTION_BASE_URL = "https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net"
PRODUCTION_FRONTEND_URL = "https://kwanpa-health-hub-six.vercel.app"  # Your frontend URL

# Get environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Set URLs based on environment
if ENVIRONMENT == "development":
    BASE_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:8081"
else:
    BASE_URL = PRODUCTION_BASE_URL
    FRONTEND_URL = PRODUCTION_FRONTEND_URL

# Email verification URLs
EMAIL_VERIFICATION_URL = f"{BASE_URL}/auth/verify-email-page"
PASSWORD_RESET_URL = f"{FRONTEND_URL}/reset-password"