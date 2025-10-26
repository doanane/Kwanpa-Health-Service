from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User, UserProfile, UserDevice
from app.schemas.user import UserProfileCreate, UserProfileResponse, UserDeviceCreate, UserDeviceResponse

router = APIRouter(prefix="/users", tags=["users"])

# Ensure upload directory exists
os.makedirs("uploads", exist_ok=True)

@router.post("/complete-profile", response_model=UserProfileResponse)
async def complete_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if existing_profile:
       
        for field, value in profile_data.dict().items():
            setattr(existing_profile, field, value)
    else:
       
        existing_profile = UserProfile(user_id=current_user.id, **profile_data.dict())
        db.add(existing_profile)
    
    db.commit()
    db.refresh(existing_profile)
    return existing_profile

@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    return profile

@router.post("/link-device", response_model=UserDeviceResponse)
async def link_device(
    device_data: UserDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    existing_device = db.query(UserDevice).filter(
        UserDevice.user_id == current_user.id,
        UserDevice.device_id == device_data.device_id
    ).first()
    
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device already linked"
        )
    
    device = UserDevice(user_id=current_user.id, **device_data.dict())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

@router.get("/devices", response_model=list[UserDeviceResponse])
async def get_devices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    devices = db.query(UserDevice).filter(UserDevice.user_id == current_user.id).all()
    return devices

@router.delete("/devices/{device_id}")
async def unlink_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = db.query(UserDevice).filter(
        UserDevice.id == device_id,
        UserDevice.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    db.delete(device)
    db.commit()
    return {"message": "Device unlinked successfully"}