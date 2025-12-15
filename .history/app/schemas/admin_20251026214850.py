from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateDoctorRequest(BaseModel):
    doctor_id: str = Field(..., min_length=8, max_length=8, pattern='^[0-9]{8}$', description="8-digit doctor ID")
    full_name: str = Field(..., description="Doctor's full name")
    specialization: str = Field(..., description="Medical specialization")
    hospital: str = Field(..., description="Hospital or clinic name")

class CreateDoctorResponse(BaseModel):
    message: str
    doctor_id: str
    initial_password: str
    full_name: str
    specialization: str

class SuperUserAuth(BaseModel):
    superuser_password: str = Field(..., description="Superuser password")

class DoctorListResponse(BaseModel):
    doctor_id: str
    full_name: str
    specialization: str
    hospital: str
    is_active: bool
    created_at: datetime
    created_by: Optional[str] = None