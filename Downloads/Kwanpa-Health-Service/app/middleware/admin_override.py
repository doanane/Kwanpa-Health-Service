from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.admin import Admin

logger = logging.getLogger(__name__)

class AdminOverrideMiddleware:
    """Middleware to allow admins to access user endpoints"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request, call_next):
        
        public_paths = ['/docs', '/redoc', '/openapi.json', '/health', '/', '/welcome']
        if any(request.url.path.startswith(path) for path in public_paths):
            return await call_next(request)
        
        
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_type = payload.get("user_type")
                subject = payload.get("sub")
                
                
                if user_type == "admin":
                    
                    db_gen = get_db()
                    db = await anext(db_gen) if hasattr(db_gen, '__anext__') else next(db_gen)
                    
                    try:
                        admin = db.query(Admin).filter(Admin.email == subject).first()
                        if admin and admin.is_active:
                            
                            request.state.is_admin = True
                            request.state.admin_id = admin.id
                            request.state.admin_email = admin.email
                            request.state.is_superadmin = admin.is_superadmin
                            
                            logger.info(f"Admin access: {admin.email} to {request.url.path}")
                    finally:
                        if hasattr(db, 'close'):
                            db.close()
                
            except JWTError:
                pass  
        
        response = await call_next(request)
        return response