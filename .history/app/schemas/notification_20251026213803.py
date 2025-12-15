from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
fro
class NotificationBase(BaseModel):
    notification_type: str = Field(..., description="Type of notification (system, caregiver, doctor)")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")

class NotificationCreate(NotificationBase):
    sender_id: Optional[int] = Field(None, description="ID of the sender")
    sender_type: Optional[str] = Field(None, description="Type of sender")

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    sender_id: Optional[int] = None
    sender_type: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationGroupResponse(BaseModel):
    system: List[NotificationResponse]
    caregiver: List[NotificationResponse]
    doctor: List[NotificationResponse]