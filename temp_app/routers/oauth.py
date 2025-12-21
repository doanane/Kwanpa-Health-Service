
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse
from app.database import get_db
from app.auth.security import create_access_token, get_password_hash
from app.models.user import User
import os

router = APIRouter(prefix="/auth", tags=["oauth"])


config = Config('.env')
oauth = OAuth(config)


oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

@router.get("/google/login")
async def google_login(request: Request):
    """Redirect to Google OAuth"""
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")
        
        email = user_info.email
        google_id = user_info.sub
        name = user_info.name
        
        
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        if not user:
            
            user = User(
                email=email,
                username=email.split('@')[0],
                google_id=google_id,
                is_email_verified=True,  verified
                hashed_password=None  users
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            user_type="user"
        )
        
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}&user_id={user.id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")