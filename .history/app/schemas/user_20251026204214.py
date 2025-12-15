from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    login: str  # Can be email or username
    password: str

class UserResponse(UserBase):
    id: int
    patient_id: str
    is_active: bool
    is_caregiver: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileBase(BaseModel):
    full_name: str
    doctor_id: Optional[str] = None
    gender: str
    age: int = Field(..., ge=1, le=120)
    chronic_conditions: List[str] = []
    family_history: List[str] = []
    weight: int = Field(..., ge=1, le=500)
    height: int = Field(..., ge=1, le=300)
    blood_pressure: str
    heart_rate: int = Field(..., ge=1, le=200)
    blood_glucose: int = Field(..., ge=1, le=500)
    daily_habits: List[str] = []

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    bmi: Optional[int] = None
    profile_completed: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserDeviceBase(BaseModel):
    device_type: str
    device_name: str
    device_id: str

class UserDeviceCreate(UserDeviceBase):
    pass

class UserDeviceResponse(UserDeviceBase):
    id: int
    user_id: int
    connected_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str  # user, doctor, caregiver

class TokenData(BaseModel):
    user_id: Optional[int] = None
    user_type: Optional[str] = None