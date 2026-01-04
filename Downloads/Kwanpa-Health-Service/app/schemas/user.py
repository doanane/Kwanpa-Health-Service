from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email address for registration")
    username: Optional[str] = Field(None, description="Username (optional)")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email used during signup")
    password: str = Field(..., description="Password")

class SignupResponse(BaseModel):
    message: str
    user_id: int
    patient_id: str
    email: str

class UserResponse(BaseModel):
    id: int
    patient_id: str
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    is_caregiver: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileBase(BaseModel):
    full_name: str = Field(..., description="Full name of the user")
    doctor_id: Optional[str] = Field(None, description="8-digit doctor ID assigned to this user")
    gender: str = Field(..., description="Gender (male/female/other)")
    age: int = Field(..., ge=1, le=120, description="Age between 1 and 120")
    chronic_conditions: List[str] = Field(default=[], description="List of chronic conditions")
    family_history: List[str] = Field(default=[], description="Family medical history")
    weight: int = Field(..., ge=1, le=500, description="Weight in kg")
    height: int = Field(..., ge=1, le=300, description="Height in cm")
    blood_pressure: str = Field(..., description="Blood pressure reading (e.g., 120/80)")
    heart_rate: int = Field(..., ge=1, le=200, description="Resting heart rate (BPM)")
    blood_glucose: int = Field(..., ge=1, le=500, description="Blood glucose level")
    daily_habits: List[str] = Field(default=[], description="Daily habits and routines")

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    bmi: Optional[int] = None
    profile_completed: bool
    
    model_config = ConfigDict(from_attributes=True)

class UserDeviceBase(BaseModel):
    device_type: str = Field(..., description="Type of device (smartwatch, fitness_tracker, etc.)")
    device_name: str = Field(..., description="Name of the device")
    device_id: str = Field(..., description="Unique device identifier")

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

class TokenData(BaseModel):
    user_id: Optional[int] = None