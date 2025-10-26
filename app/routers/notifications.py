from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import get_current_active_user  # Fixed import
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationGroupResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=NotificationGroupResponse)
async def get_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    all_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    # Group by type
    system_notifications = [n for n in all_notifications if n.notification_type == "system"]
    caregiver_notifications = [n for n in all_notifications if n.notification_type == "caregiver"]
    doctor_notifications = [n for n in all_notifications if n.notification_type == "doctor"]
    
    return NotificationGroupResponse(
        system=system_notifications,
        caregiver=caregiver_notifications,
        doctor=doctor_notifications
    )

@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
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
    current_user: User = Depends(get_current_active_user)
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return {"unread_count": count}