
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Union, Dict
import json

from app.database import get_db
from app.auth.security import get_current_active_user_or_admin
from app.models.user import User
from app.models.admin import Admin
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationGroupResponse, NotificationCreate

router = APIRouter(prefix="/notifications", tags=["notifications"])

class NotificationConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ User {user_id} connected to notification WebSocket")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        print(f"❌ User {user_id} disconnected from notification WebSocket")
    
    async def send_notification(self, user_id: int, notification: dict):
        """Send notification to specific user if they're connected"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(notification)
                return True
            except Exception as e:
                print(f"❌ Error sending notification to user {user_id}: {e}")
                self.disconnect(user_id)
        return False
    
    async def broadcast_to_caregivers(self, patient_id: int, notification: dict, db: Session):
        """Send notification to all caregivers of a patient"""
        from app.models.caregiver import CaregiverRelationship
        
        relationships = db.query(CaregiverRelationship).filter(
            CaregiverRelationship.patient_id == patient_id,
            CaregiverRelationship.status == "approved"
        ).all()
        
        for rel in relationships:
            await self.send_notification(rel.caregiver_id, notification)

notification_manager = NotificationConnectionManager()

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

@router.post("/create")
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    """Create a new notification (for internal use or admin)"""
    # For now, only allow certain user types to create notifications
    # You can add more sophisticated permission checks here
    
    notification = Notification(
        user_id=notification_data.user_id if hasattr(notification_data, 'user_id') else current.id,
        notification_type=notification_data.notification_type,
        title=notification_data.title,
        message=notification_data.message,
        sender_id=notification_data.sender_id,
        sender_type=notification_data.sender_type
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send real-time notification via WebSocket
    await notification_manager.send_notification(notification.user_id, {
        "type": "new_notification",
        "notification": {
            "id": notification.id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "created_at": notification.created_at.isoformat(),
            "is_read": False
        }
    })
    
    return NotificationResponse.from_orm(notification)

# WebSocket endpoint for real-time notifications
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket connection for real-time notifications"""
    await notification_manager.connect(user_id, websocket)
    
    try:
        while True:
            # Receive messages from client (keep-alive pings)
            data = await websocket.receive_json()
            
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        notification_manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        notification_manager.disconnect(user_id)

# Helper function to send notification (can be imported by other routers)
async def send_notification_to_user(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    sender_id: int = None,
    sender_type: str = None,
    db: Session = None
):
    """Helper function to create and send notification"""
    if not db:
        return
    
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        sender_id=sender_id,
        sender_type=sender_type
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send via WebSocket
    await notification_manager.send_notification(user_id, {
        "type": "new_notification",
        "notification": {
            "id": notification.id,
            "notification_type": notification.notification_type,
            "title": notification.title,
            "message": notification.message,
            "created_at": notification.created_at.isoformat(),
            "is_read": False
        }
    })
    
    return notification