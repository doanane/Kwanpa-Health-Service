from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
import os

router = APIRouter(prefix="/test-oauth", tags=["test-oauth"])

@router.get("/config")
async def get_oauth_config():
    """Show current OAuth configuration"""
    config = {
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", "Not set"),
        "GOOGLE_REDIRECT_URI": os.getenv("GOOGLE_REDIRECT_URI", "Not set"),
        "BASE_URL": os.getenv("BASE_URL", "Not set"),
    }
    
    # Check for double slashes
    if config["GOOGLE_REDIRECT_URI"] != "Not set":
        if "//auth" in config["GOOGLE_REDIRECT_URI"]:
            config["DOUBLE_SLASH_ERROR"] = "YES - Found //auth in redirect URI"
        else:
            config["DOUBLE_SLASH_ERROR"] = "NO - Redirect URI looks good"
    
    return config

@router.get("/auth-url")
async def get_auth_url():
    """Generate Google OAuth URL for testing"""
    from app.config import settings
    
    try:
        # Construct Google OAuth URL
        base_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        auth_url = f"{base_auth_url}?{query_string}"
        
        return {
            "auth_url": auth_url,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "has_double_slash": "//auth" in settings.GOOGLE_REDIRECT_URI
        }
        
    except Exception as e:
        return {"error": str(e), "message": "Check your OAuth configuration"}
