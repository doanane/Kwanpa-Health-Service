from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.caregiver import Doctor

# Different token URLs for different user types
oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)
oauth2_scheme_doctor = OAuth2PasswordBearer(tokenUrl="doctors/login", auto_error=False)

def create_access_token(data: dict, user_type: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "user_type": user_type})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme_user), 
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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
    token: str = Depends(oauth2_scheme_doctor), 
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
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

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_doctor(current_doctor: Doctor = Depends(get_current_doctor)):
    if not current_doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")
    return current_doctor