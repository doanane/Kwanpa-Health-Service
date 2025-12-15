from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    notification_type: str
    title: str
    message: str

class NotificationCreate(NotificationBase):
    sender_id: Optional[int] = None
    sender_type: Optional[str] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    sender_id: Optional[int] = None
    sender_type: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationGroupResponse(BaseModel):
    system: list[NotificationResponse]
    caregiver: list[NotificationResponse]
    doctor: list[NotificationResponse]