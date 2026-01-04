# back/app/routers/messages.py
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Dict
from datetime import datetime
import json

from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver import Message, CaregiverRelationship
from app.schemas.message import (
    MessageCreate, MessageResponse, ConversationResponse, 
    MessageReadRequest, TypingStatus
)

router = APIRouter(prefix="/messages", tags=["messages"])

# WebSocket connection manager for real-time messaging
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.typing_status: Dict[int, Dict] = {}  # {user_id: {with_user_id: is_typing}}
    
    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"✅ User {user_id} connected to messaging WebSocket")
    
    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.typing_status:
            del self.typing_status[user_id]
        print(f"❌ User {user_id} disconnected from messaging WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user if they're connected"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                print(f"❌ Error sending to user {user_id}: {e}")
                self.disconnect(user_id)
        return False
    
    async def broadcast_typing(self, user_id: int, to_user_id: int, is_typing: bool):
        """Broadcast typing status"""
        if to_user_id in self.active_connections:
            await self.send_personal_message({
                "type": "typing",
                "from_user_id": user_id,
                "is_typing": is_typing
            }, to_user_id)
    
    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

manager = ConnectionManager()

# Helper function to verify caregiver-patient relationship
async def verify_can_message(sender_id: int, receiver_id: int, db: Session) -> bool:
    """Check if sender can message receiver"""
    # Check if they have an approved caregiver relationship (either direction)
    relationship = db.query(CaregiverRelationship).filter(
        or_(
            and_(
                CaregiverRelationship.caregiver_id == sender_id,
                CaregiverRelationship.patient_id == receiver_id
            ),
            and_(
                CaregiverRelationship.caregiver_id == receiver_id,
                CaregiverRelationship.patient_id == sender_id
            )
        ),
        CaregiverRelationship.status == "approved"
    ).first()
    
    return relationship is not None

# REST API Endpoints

@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a new message"""
    # Verify receiver exists
    receiver = db.query(User).filter(User.id == message_data.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Verify relationship (caregiver-patient connection)
    can_message = await verify_can_message(current_user.id, message_data.receiver_id, db)
    if not can_message:
        raise HTTPException(
            status_code=403, 
            detail="You can only message users you have an approved relationship with"
        )
    
    # Create message
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message_data.receiver_id,
        content=message_data.content,
        is_read=False
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Send real-time notification via WebSocket
    await manager.send_personal_message({
        "type": "new_message",
        "message": {
            "id": db_message.id,
            "sender_id": current_user.id,
            "sender_name": f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
            "sender_email": current_user.email,
            "content": db_message.content,
            "created_at": db_message.created_at.isoformat(),
            "is_read": False
        }
    }, message_data.receiver_id)
    
    # Prepare response
    response = MessageResponse(
        id=db_message.id,
        sender_id=db_message.sender_id,
        receiver_id=db_message.receiver_id,
        content=db_message.content,
        is_read=db_message.is_read,
        created_at=db_message.created_at,
        sender_name=f"{current_user.first_name or ''} {current_user.last_name or ''}".strip() or current_user.email,
        sender_email=current_user.email,
        receiver_name=f"{receiver.first_name or ''} {receiver.last_name or ''}".strip() or receiver.email,
        receiver_email=receiver.email
    )
    
    return response

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user"""
    # Get all users current user has messaged or been messaged by
    sent_messages = db.query(Message.receiver_id).filter(
        Message.sender_id == current_user.id
    ).distinct().subquery()
    
    received_messages = db.query(Message.sender_id).filter(
        Message.receiver_id == current_user.id
    ).distinct().subquery()
    
    # Get unique user IDs
    conversation_user_ids = db.query(User.id).filter(
        or_(
            User.id.in_(sent_messages),
            User.id.in_(received_messages)
        )
    ).all()
    
    conversations = []
    for (user_id,) in conversation_user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            continue
        
        # Get last message between users
        last_message = db.query(Message).filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
                and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).first()
        
        # Count unread messages from this user
        unread_count = db.query(func.count(Message.id)).filter(
            Message.sender_id == user_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False
        ).scalar()
        
        # Determine user type
        user_type = "doctor" if user.email and "doctor" in user.email.lower() else \
                    ("caregiver" if user.is_caregiver else "patient")
        
        conversation = ConversationResponse(
            user_id=user.id,
            user_name=f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username or user.email,
            user_email=user.email,
            user_type=user_type,
            patient_id=user.patient_id,
            caregiver_id=user.caregiver_id,
            last_message=last_message.content if last_message else None,
            last_message_time=last_message.created_at if last_message else None,
            unread_count=unread_count,
            is_online=manager.is_user_online(user.id)
        )
        conversations.append(conversation)
    
    # Sort by last message time
    conversations.sort(key=lambda x: x.last_message_time or datetime.min, reverse=True)
    
    return conversations

@router.get("/conversation/{user_id}", response_model=List[MessageResponse])
async def get_conversation_messages(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages in a conversation with specific user"""
    # Verify user exists
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify relationship
    can_message = await verify_can_message(current_user.id, user_id, db)
    if not can_message:
        raise HTTPException(
            status_code=403,
            detail="You can only view conversations with users you have an approved relationship with"
        )
    
    # Get messages
    messages = db.query(Message).filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    
    # Reverse to get chronological order
    messages.reverse()
    
    # Prepare response with user details
    response = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        receiver = db.query(User).filter(User.id == msg.receiver_id).first()
        
        response.append(MessageResponse(
            id=msg.id,
            sender_id=msg.sender_id,
            receiver_id=msg.receiver_id,
            content=msg.content,
            is_read=msg.is_read,
            created_at=msg.created_at,
            sender_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else None,
            sender_email=sender.email if sender else None,
            receiver_name=f"{receiver.first_name or ''} {receiver.last_name or ''}".strip() if receiver else None,
            receiver_email=receiver.email if receiver else None
        ))
    
    return response

@router.post("/mark-read")
async def mark_messages_as_read(
    read_request: MessageReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark messages as read"""
    messages = db.query(Message).filter(
        Message.id.in_(read_request.message_ids),
        Message.receiver_id == current_user.id
    ).all()
    
    for message in messages:
        message.is_read = True
    
    db.commit()
    
    return {"message": f"Marked {len(messages)} messages as read"}

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total unread message count"""
    count = db.query(func.count(Message.id)).filter(
        Message.receiver_id == current_user.id,
        Message.is_read == False
    ).scalar()
    
    return {"unread_count": count}

# WebSocket endpoint for real-time messaging
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    """WebSocket connection for real-time messaging"""
    await manager.connect(user_id, websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "typing":
                # Broadcast typing status
                to_user_id = data.get("to_user_id")
                is_typing = data.get("is_typing", False)
                await manager.broadcast_typing(user_id, to_user_id, is_typing)
            
            elif message_type == "ping":
                # Keep connection alive
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)
