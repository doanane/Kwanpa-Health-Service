from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.caregiver import Doctor
from app.models.admin import Admin
from typing import Optional, Union
from sqlalchemy.orm import Session
from app.models.admin import Admin


import re
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, status
from app.auth.hashing import verify_password, get_password_hash

security_scheme = HTTPBearer(auto_error=False)


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

def check_password_history(user_id: int, new_password: str, db: Session) -> bool:
    """Check if password was used before"""
    # In production, store password history
    return True  # For hackathon, skip this

def create_access_token(data: dict, user_type: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "user_type": user_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# Update the get_current_user function to handle admin tokens too
async def get_current_user_or_admin(
    token: Optional[str] = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> Union[User, Admin]:
    """
    Universal authentication that accepts both user and admin tokens
    Returns either User or Admin object based on token type
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        subject: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if subject is None:
            raise credentials_exception
        
        if user_type == "user":
            # Regular user token
            user = db.query(User).filter(User.id == int(subject)).first()
            if user is None or not user.is_active:
                raise credentials_exception
            return user
            
        elif user_type == "admin":
            # Admin token
            admin = db.query(Admin).filter(Admin.email == subject).first()
            if admin is None or not admin.is_active:
                raise credentials_exception
            return admin
            
        else:
            # Doctor token or other types
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

# Create a universal "get current active" function
async def get_current_active_user_or_admin(
    current: Union[User, Admin] = Depends(get_current_user_or_admin)
):
    """Get current active user or admin"""
    if hasattr(current, 'is_active'):
        if not current.is_active:
            raise HTTPException(status_code=400, detail="Account is inactive")
    return current

# Keep existing functions for backward compatibility
async def get_current_user(token: Optional[str] = Depends(security_scheme), db: Session = Depends(get_db)) -> User:
    """Original function - only accepts user tokens"""
    return await get_current_user_or_admin(token, db)

async def get_current_admin(token: Optional[str] = Depends(security_scheme), db: Session = Depends(get_db)) -> Admin:
    """Original function - only accepts admin tokens"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if admin_email is None or user_type != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == admin_email).first()
    if admin is None or not admin.is_active:
        raise credentials_exception
    
    return admin



async def get_current_user(
    token: Optional[str] = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None or user_type != "user":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_doctor(
    token: Optional[str] = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> Doctor:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        doctor_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if doctor_id is None or user_type != "doctor":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if doctor is None:
        raise credentials_exception
    return doctor

async def get_current_admin(
    token: Optional[str] = Depends(security_scheme), 
    db: Session = Depends(get_db)
) -> Admin:
    """Get current admin from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        admin_email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if admin_email is None or user_type != "admin":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.email == admin_email).first()
    if admin is None or not admin.is_active:
        raise credentials_exception
    
    return admin

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_doctor(current_doctor: Doctor = Depends(get_current_doctor)):
    if not current_doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")
    return current_doctor

async def get_current_active_admin(current_admin: Admin = Depends(get_current_admin)):
    """Get current active admin"""
    if not current_admin.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin")
    return current_admin

# Export password functions
__all__ = [
    'create_access_token',
    'get_current_user',
    'get_current_doctor', 
    'get_current_admin',
    'get_current_active_user',
    'get_current_active_doctor',
    'get_current_active_admin',
    'verify_password',
    'get_password_hash'
]