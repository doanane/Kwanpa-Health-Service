from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserProfileBase(BaseModel):
    full_name: str
    caregiver_id: Optional[str] = None
    doctor_id: Optional[str] = None
    gender: str
    age: int
    chronic_conditions: List[str] = []
    family_history: List[str] = []
    weight: int
    height: int
    bmi: Optional[int] = None
    blood_pressure: str
    heart_rate: int
    blood_glucose: int
    daily_habits: List[str] = []

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    
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

class TokenData(BaseModel):
    user_id: Optional[int] = None