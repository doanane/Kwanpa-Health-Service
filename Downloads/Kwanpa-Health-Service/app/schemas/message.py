# back/app/schemas/message.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    receiver_id: int = Field(..., description="ID of message recipient")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_email: Optional[str] = None
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    user_id: int
    user_name: str
    user_email: str
    user_type: str  # "patient", "caregiver", "doctor"
    patient_id: Optional[str] = None
    caregiver_id: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0
    is_online: bool = False

class MessageReadRequest(BaseModel):
    message_ids: List[int] = Field(..., description="List of message IDs to mark as read")

class TypingStatus(BaseModel):
    user_id: int
    is_typing: bool
    conversation_with: int  # user_id of the other person
