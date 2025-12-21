from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import httpx
from datetime import datetime, timedelta
import secrets
import logging
import urllib.parse
import os
from typing import Optional

from app.database import get_db
from app.auth.security import create_access_token, get_current_active_user
from app.models.user import User
from app.models.auth import UserSession
from app.config import settings

router = APIRouter(prefix="/auth/google", tags=["google_oauth"])
logger = logging.getLogger(__name__)

# Configuration - Get from environment or settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Determine redirect URI based on environment
if "localhost" in BASE_URL or "127.0.0.1" in BASE_URL:
    # Local development
    GOOGLE_REDIRECT_URI = f"{BASE_URL}/auth/google/callback"
else:
    # Production - use your backend URL
    GOOGLE_REDIRECT_URI = f"{BASE_URL}/auth/google/callback"

# Google endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def is_google_configured() -> bool:
    """Check if Google OAuth is properly configured"""
    return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

@router.get("/login")
async def google_login(request: Request):
    """
    Start Google OAuth flow
    This will redirect to Google login page
    """
    if not is_google_configured():
        logger.error("Google OAuth not configured")
        return JSONResponse(
            status_code=503,
            content={
                "error": "Google OAuth not configured",
                "message": "Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment variables"
            }
        )
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build Google OAuth URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "state": state,
        "access_type": "offline",
        "prompt": "select_account"
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    
    # Store state in session/cookie
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=not BASE_URL.startswith("http://localhost"),  # Secure only in production
        samesite="lax",
        max_age=300  # 5 minutes
    )
    
    return response

@router.get("/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback
    This endpoint is called by Google after user authentication
    """
    # Check for errors
    if error:
        logger.error(f"Google OAuth error: {error} - {error_description}")
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error={error}&message={error_description}"
        )
    
    if not code:
        logger.error("No authorization code received")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=no_code&message=No authorization code received"
        )
    
    # Verify state (CSRF protection)
    stored_state = request.cookies.get("oauth_state")
    if not stored_state or stored_state != state:
        logger.warning(f"State mismatch: stored={stored_state}, received={state}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=state_mismatch&message=Security validation failed"
        )
    
    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        
        if token_response.status_code != 200:
            error_data = token_response.json()
            logger.error(f"Token exchange failed: {error_data}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=token_exchange_failed&message=Failed to get access token"
            )
        
        tokens = token_response.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            logger.error("No access token in response")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=no_access_token&message=No access token received"
            )
        
        # Get user info from Google
        async with httpx.AsyncClient(timeout=30.0) as client:
            user_response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
        
        if user_response.status_code != 200:
            logger.error(f"Failed to get user info: {user_response.text}")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=user_info_failed&message=Failed to get user information"
            )
        
        user_info = user_response.json()
        
        # Extract user information
        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name", "")
        given_name = user_info.get("given_name", "")
        
        if not email:
            logger.error("No email in user info")
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=no_email&message=No email received from Google"
            )
        
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        is_new_user = False
        
        if not user:
            # Create new user
            username = email.split('@')[0]
            # Ensure username is unique
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                username = f"{username}_{secrets.token_hex(4)}"
            
            user = User(
                email=email,
                username=username,
                google_id=google_id,
                is_email_verified=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
            logger.info(f"New user created via Google OAuth: {email}")
        
        else:
            # Update existing user
            if not user.google_id:
                user.google_id = google_id
            user.is_email_verified = True
            user.last_login = datetime.utcnow()
            db.commit()
            logger.info(f"Existing user logged in via Google OAuth: {email}")
        
        # Create JWT token
        jwt_token = create_access_token(
            data={"sub": str(user.id)},
            user_type="user",
            expires_delta=timedelta(days=7)
        )
        
        # Create refresh token
        refresh_token = secrets.token_urlsafe(64)
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        device_info = request.headers.get("User-Agent", "Unknown")
        ip_address = request.client.host if request.client else "Unknown"
        
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        
        db.add(session)
        db.commit()
        
        # Redirect to frontend with tokens
        # Using fragment identifier (#) for security
        redirect_params = {
            "access_token": jwt_token,
            "refresh_token": refresh_token,
            "user_id": str(user.id),
            "email": email,
            "username": user.username,
            "is_new_user": str(is_new_user).lower(),
            "expires_in": "604800"  # 7 days in seconds
        }
        
        params_str = urllib.parse.urlencode(redirect_params)
        redirect_url = f"{FRONTEND_URL}/dashboard#auth_success&{params_str}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Google OAuth error: {str(e)}", exc_info=True)
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=server_error&message=Authentication failed"
        )

@router.post("/token-auth")
async def google_token_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Alternative: Authenticate with Google ID token (for SPA)
    This doesn't require redirect URI setup
    """
    try:
        data = await request.json()
        google_token = data.get("id_token")
        
        if not google_token:
            raise HTTPException(
                status_code=400,
                detail="Google ID token is required"
            )
        
        # Verify Google token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Invalid Google token"
            )
        
        token_info = response.json()
        
        # Verify token audience
        if token_info.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=400,
                detail="Token audience mismatch"
            )
        
        email = token_info.get("email")
        google_id = token_info.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=400,
                detail="No email in token"
            )
        
        # Find or create user
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        is_new_user = False
        
        if not user:
            # Create new user
            username = email.split('@')[0]
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                username = f"{username}_{secrets.token_hex(4)}"
            
            user = User(
                email=email,
                username=username,
                google_id=google_id,
                is_email_verified=True,
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            is_new_user = True
        
        else:
            # Update existing user
            if not user.google_id:
                user.google_id = google_id
            user.is_email_verified = True
            user.last_login = datetime.utcnow()
            db.commit()
        
        # Create JWT token
        jwt_token = create_access_token(
            data={"sub": str(user.id)},
            user_type="user",
            expires_delta=timedelta(days=7)
        )
        
        return {
            "success": True,
            "access_token": jwt_token,
            "token_type": "bearer",
            "expires_in": 604800,  # 7 days
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "patient_id": user.patient_id,
                "is_email_verified": user.is_email_verified,
                "is_new_user": is_new_user
            }
        }
        
    except Exception as e:
        logger.error(f"Google token auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/config")
async def get_google_config():
    """Get Google OAuth configuration (for debugging)"""
    return {
        "configured": is_google_configured(),
        "client_id_exists": bool(GOOGLE_CLIENT_ID),
        "client_secret_exists": bool(GOOGLE_CLIENT_SECRET),
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "base_url": BASE_URL,
        "frontend_url": FRONTEND_URL,
        "environment": "production" if "localhost" not in BASE_URL else "development"
    }