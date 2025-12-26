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

async def get_current_user_id(current_user: Depends(get_current_user)):
    return current_user.id

async def get_notifications(
    db: Session = Depends(get_db), 
    current_user_id: int = Depends(get_current_user_id)
):
    return db.query(Notification).filter(
        Notification.user_id == current_user_id
    ).all()