
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class CaregiverSignupRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    caregiver_type: str = Field(..., description="family, friend, or professional")
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    agree_to_terms: bool = Field(..., description="Must agree to terms")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # Basic phone validation - adjust for your country
            if not re.match(r'^\+?[1-9]\d{1,14}$', v):
                raise ValueError('Invalid phone number format')
        return v
    
    @validator('caregiver_type')
    def validate_caregiver_type(cls, v):
        valid_types = ['family', 'friend', 'professional']
        if v.lower() not in valid_types:
            raise ValueError(f'Caregiver type must be one of: {", ".join(valid_types)}')
        return v.lower()

class CaregiverSignupResponse(BaseModel):
    caregiver_id: str
    email: str
    first_name: str
    last_name: str
    caregiver_type: str
    message: str
    access_token: Optional[str] = None