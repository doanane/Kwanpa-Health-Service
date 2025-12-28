
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union

from app.database import get_db
from app.auth.security import get_current_active_user_or_admin
from app.models.user import User
from app.models.admin import Admin
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationGroupResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=NotificationGroupResponse)
async def get_notifications(
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    
    
    if isinstance(current, Admin):
        return NotificationGroupResponse(
            system=[],
            caregiver=[],
            doctor=[]
        )
    
    
    notifications = db.query(Notification).filter(
        Notification.user_id == current.id
    ).order_by(Notification.created_at.desc()).all()
    
    
    system = [n for n in notifications if n.notification_type == "system"]
    caregiver = [n for n in notifications if n.notification_type == "caregiver"]
    doctor = [n for n in notifications if n.notification_type == "doctor"]
    
    return NotificationGroupResponse(
        system=system,
        caregiver=caregiver,
        doctor=doctor
    )

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    if isinstance(current, Admin):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins don't have user notifications"
        )
    
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    if isinstance(current, Admin):
        return {"unread_count": 0}
    
    count = db.query(Notification).filter(
        Notification.user_id == current.id,
        Notification.is_read == False
    ).count()
    
    return {"unread_count": count}