from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import (
    get_current_user,
    get_current_active_user, 
    get_current_doctor,
    get_current_active_doctor,
    get_current_admin,
    get_current_active_admin,
    get_current_user_or_admin,
    get_current_active_user_or_admin
)

__all__ = [
    "get_current_user",
    "get_current_active_user", 
    "get_current_doctor",
    "get_current_active_doctor",
    "get_current_admin",
    "get_current_active_admin",
    "get_current_user_or_admin",
    "get_current_active_user_or_admin"
]