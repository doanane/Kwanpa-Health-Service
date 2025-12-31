
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from sqlalchemy.orm import Session
import re
from app.config import settings
from app.database import get_db
from app.auth.hashing import verify_password, get_password_hash



security = HTTPBearer()  

def validate_password_strength(password: str) -> bool:
    """Enforce strong password policy"""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def create_access_token(data: dict, user_type: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "user_type": user_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user_or_admin(
    
    auth: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    """Get current user or admin from JWT token"""
    
    
    token = auth.credentials 

    
    from app.models.user import User
    from app.models.caregiver import Doctor
    from app.models.admin import Admin

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None:
            raise credentials_exception

        if user_type == "admin":
            admin = db.query(Admin).filter(Admin.email == user_id).first()
            if admin is None:
                raise credentials_exception
            return admin
            
        elif user_type == "doctor":
            doctor = db.query(Doctor).filter(Doctor.doctor_id == user_id).first()
            if doctor is None:
                raise credentials_exception
            return doctor
            
        elif user_type == "caregiver":
            
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user is None:
                raise credentials_exception
            return user
            
        else:
            
            try:
                u_id = int(user_id)
                user = db.query(User).filter(User.id == u_id).first()
            except ValueError:
                
                user = db.query(User).filter(User.email == user_id).first()
                
            if user is None:
                raise credentials_exception
            return user
            
    except JWTError:
        raise credentials_exception

async def get_current_active_user_or_admin(
    current = Depends(get_current_user_or_admin)
):
    """Get current active user or admin"""
    if hasattr(current, 'is_active') and not current.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")
    return current

async def get_current_user(
    current = Depends(get_current_user_or_admin)
):
    """Get current user only (casts to User model)"""
    from app.models.user import User
    
    if not isinstance(current, User):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint requires user authentication"
        )
    return current

async def get_current_doctor(
    current = Depends(get_current_user_or_admin)
):
    """Get current doctor only"""
    from app.models.caregiver import Doctor
    
    if not isinstance(current, Doctor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint requires doctor authentication"
        )
    return current

async def get_current_admin(
    current = Depends(get_current_user_or_admin)
):
    """Get current admin only"""
    from app.models.admin import Admin
    
    if not isinstance(current, Admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint requires admin authentication"
        )
    return current

async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_doctor(current_doctor = Depends(get_current_doctor)):
    if not current_doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")
    return current_doctor

async def get_current_active_admin(current_admin = Depends(get_current_admin)):
    if not current_admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin")
    return current_admin