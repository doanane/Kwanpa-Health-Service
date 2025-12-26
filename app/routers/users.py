
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import os
import shutil
from pydantic import BaseModel
from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User, UserProfile, UserDevice
from app.services.storage_service import storage_service
from app.models.health import HealthData 
import logging
from app.models.emergency import EmergencyContact
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])



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
    profile_image_url: Optional[str]
    created_at: datetime

class UserInfoResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    patient_id: Optional[str]
    is_caregiver: bool
    caregiver_id: Optional[str]
    is_email_verified: bool
    phone_number: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

class UploadImageResponse(BaseModel):
    message: str
    image_url: str
    user_id: int
    filename: str



@router.get("/test")
async def test_endpoint():
    """Test users endpoint"""
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
        "profile_image_url": getattr(profile, 'profile_image_url', None),
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

@router.post("/upload-profile-image", response_model=UploadImageResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    """Upload profile image"""
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (JPG, PNG, GIF, WebP)"
        )
    
    max_size = 5 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    upload_dir = "uploads/profile_images"
    os.makedirs(upload_dir, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"user_{current_user.id}_{timestamp}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    try:
        # Use the service instead of manual file saving
        image_url = await storage_service.upload_file(file, folder="profile_images")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
     
    
    profile.profile_image_url = image_url
    db.commit()
    
    return {
        "message": "Profile image uploaded successfully",
        "image_url": image_url,
        "user_id": current_user.id,
        "filename": file.filename
    }

@router.get("/profile-image")
async def get_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's profile image URL"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile or not getattr(profile, 'profile_image_url', None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile image found"
        )
    
    return {
        "image_url": profile.profile_image_url,
        "user_id": current_user.id,
        "full_url": f"https://hewal3-backend-api-aya3dzgefte4b3c3.southafricanorth-01.azurewebsites.net{profile.profile_image_url}"
    }

@router.get("/me", response_model=UserInfoResponse)
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

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=2, description="Search by email, username, or patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for users (patients or caregivers)"""
    if not query or len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters"
        )
    
    users = db.query(User).filter(
        (User.email.ilike(f"%{query}%")) |
        (User.username.ilike(f"%{query}%")) |
        (User.patient_id.ilike(f"%{query}%")) |
        (User.caregiver_id.ilike(f"%{query}%"))
    ).limit(20).all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "patient_id": user.patient_id,
            "caregiver_id": getattr(user, 'caregiver_id', None),
            "is_caregiver": getattr(user, 'is_caregiver', False),
            "is_active": user.is_active
        }
        for user in users
    ]

@router.get("/emergency-contacts")
async def get_emergency_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's emergency contacts"""
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": contact.id,
            "name": contact.name,
            "phone": contact.phone_number,  # Changed from contact.phone
            "relationship": contact.relationship_type,  # Changed from contact.relationship
            "is_primary": contact.is_primary
        }
        for contact in contacts
    ]

@router.post("/emergency-contacts")
async def add_emergency_contact(
    name: str = Form(...),
    phone: str = Form(...),
    relationship: str = Form(...),
    is_primary: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add emergency contact"""
    contact = EmergencyContact(
        user_id=current_user.id,
        name=name,
        phone_number=phone,  # Changed from phone
        relationship_type=relationship,  # Changed from relationship
        is_primary=is_primary
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return {
        "message": "Emergency contact added",
        "contact_id": contact.id,
        "name": contact.name
    }

@router.delete("/emergency-contacts/{contact_id}")
async def delete_emergency_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete emergency contact"""
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Emergency contact deleted"}