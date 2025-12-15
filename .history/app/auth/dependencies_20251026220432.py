from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.security import get_current_user, get_current_active_user, get_current_doctor, get_current_active_doctor

# Re-export the security functions for backward compatibility
__all__ = [
    "get_current_user",
    "get_current_active_user", 
    "get_current_doctor",
    "get_current_active_doctor"
]