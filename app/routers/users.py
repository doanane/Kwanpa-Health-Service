from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import os
import shutil
from pydantic import BaseModel
from app.database import get_db
from app.auth.security import get_current_user 
from app.models.user import User, UserProfile, UserDevice
# from app.models.health import HealthData, EmergencyContact, EmergencyEvent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

# Pydantic Models
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    chronic_conditions: Optional[List[str]] = None
    family_history: Optional[List[str]] = None
    weight: Optional[int] = None
    height: Optional[int] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    blood_glucose: Optional[int] = None
    daily_habits: Optional[List[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None

class ProfileResponse(BaseModel):
    user_id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    gender: Optional[str]
    age: Optional[int]
    chronic_conditions: List[str]
    family_history: List[str]
    weight: Optional[int]
    height: Optional[int]
    bmi: Optional[float]
    blood_pressure: Optional[str]
    heart_rate: Optional[int]
    blood_glucose: Optional[int]
    daily_habits: List[str]
    profile_completed: bool
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    emergency_contact_relationship: Optional[str]
    is_caregiver: bool
    patient_id: Optional[str]
    created_at: datetime

# Endpoints

@router.get("/test")
async def test_users():
    """Test endpoint for users router"""
    return {"message": "Users router is working", "timestamp": datetime.utcnow().isoformat()}

@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
       
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return {
        "user_id": current_user.id,
        "email": current_user.email or "",
        "username": current_user.username,
        "full_name": profile.full_name,
        "gender": profile.gender,
        "age": profile.age,
        "chronic_conditions": profile.chronic_conditions or [],
        "family_history": profile.family_history or [],
        "weight": profile.weight,
        "height": profile.height,
        "bmi": profile.bmi,
        "blood_pressure": profile.blood_pressure,
        "heart_rate": profile.heart_rate,
        "blood_glucose": profile.blood_glucose,
        "daily_habits": profile.daily_habits or [],
        "profile_completed": profile.profile_completed or False,
        "emergency_contact_name": profile.emergency_contact_name,
        "emergency_contact_phone": profile.emergency_contact_phone,
        "emergency_contact_relationship": profile.emergency_contact_relationship,
        "is_caregiver": getattr(current_user, 'is_caregiver', False),
        "patient_id": current_user.patient_id,
        "created_at": current_user.created_at
    }

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Update user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
   
    update_fields = profile_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if value is not None:
            setattr(profile, field, value)
    
   
    if profile_data.weight and profile_data.height:
        height_m = profile_data.height / 100 
        if height_m > 0:
            profile.bmi = round(profile_data.weight / (height_m ** 2), 1)
    
   
    essential_fields = ['full_name', 'gender', 'age', 'weight', 'height']
    if all(getattr(profile, field, None) for field in essential_fields):
        profile.profile_completed = True
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile updated successfully", "profile_completed": profile.profile_completed}

@router.post("/profile/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Upload profile photo"""
   
    upload_dir = "uploads/profile_photos"
    os.makedirs(upload_dir, exist_ok=True)
    
   
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
   
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
   
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    profile.photo_url = f"/uploads/profile_photos/{filename}"
    db.commit()
    
    return {"message": "Profile photo uploaded", "photo_url": profile.photo_url}

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user) 
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "patient_id": current_user.patient_id,
        "is_caregiver": getattr(current_user, 'is_caregiver', False),
        "caregiver_id": getattr(current_user, 'caregiver_id', None),
        "is_email_verified": current_user.is_email_verified,
        "phone_number": current_user.phone_number,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }

@router.get("/devices")
async def get_user_devices(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Get user's registered devices"""
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    
    return [
        {
            "id": device.id,
            "device_type": device.device_type,
            "device_name": device.device_name,
            "device_id": device.device_id,
            "connected_at": device.connected_at
        }
        for device in devices
    ]

@router.post("/devices")
async def register_device(
    device_type: str = Form(...),
    device_name: str = Form(...),
    device_id: str = Form(...),
    fcm_token: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Register a new device for the user"""
   
    existing = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.device_id == device_id
    ).first()
    
    if existing:
       
        existing.device_type = device_type
        existing.device_name = device_name
        existing.fcm_token = fcm_token
        db.commit()
        return {"message": "Device updated", "device_id": existing.id}
    
   
    device = UserDevice(
        user_id=current_user.id,
        device_type=device_type,
        device_name=device_name,
        device_id=device_id,
        fcm_token=fcm_token
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return {"message": "Device registered", "device_id": device.id}

@router.delete("/devices/{device_id}")
async def unregister_device(
    device_id: str,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Unregister a device"""
    device = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.device_id == device_id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    db.delete(device)
    db.commit()
    
    return {"message": "Device unregistered"}