# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.caregiver import Doctor
from app.models.admin import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user_or_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        if user_type == "admin":
            admin = db.query(Admin).filter(Admin.email == user_id).first()
            if not admin:
                raise HTTPException(status_code=401, detail="Admin not found")
            return admin
        elif user_type == "doctor":
            doctor = db.query(Doctor).filter(Doctor.doctor_id == user_id).first()
            if not doctor:
                raise HTTPException(status_code=401, detail="Doctor not found")
            return doctor
        else:
            # Handle string vs int ID issues
            try:
                u_id = int(user_id)
                user = db.query(User).filter(User.id == u_id).first()
            except ValueError:
                # Fallback for old tokens or different ID schemes
                user = db.query(User).filter(User.email == user_id).first()
                
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            return user
            
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

async def get_current_active_user_or_admin(current = Depends(get_current_user_or_admin)):
    if not current.is_active:
        raise HTTPException(status_code=400, detail="Inactive account")
    return current

async def get_current_user(current = Depends(get_current_user_or_admin)) -> User:
    if not isinstance(current, User):
        raise HTTPException(status_code=403, detail="Not a user")
    return current

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_doctor(current = Depends(get_current_user_or_admin)) -> Doctor:
    if not isinstance(current, Doctor):
        raise HTTPException(status_code=403, detail="Not a doctor")
    return current

async def get_current_active_doctor(current_doctor: Doctor = Depends(get_current_doctor)) -> Doctor:
    if not current_doctor.is_active:
        raise HTTPException(status_code=400, detail="Inactive doctor")
    return current_doctor

async def get_current_active_admin(current = Depends(get_current_user_or_admin)) -> Admin:
    if not isinstance(current, Admin):
        raise HTTPException(status_code=403, detail="Not an admin")
    if not current.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin")
    return current