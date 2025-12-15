from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class DoctorCreate(BaseModel):
    doctor_id: str = Field(..., min_length=8, max_length=8, pattern='^[0-9]{8}$', description="8-digit doctor ID")
    full_name: str = Field(..., description="Doctor's full name")
    specialization: str = Field(..., description="Medical specialization")
    hospital: str = Field(..., description="Hospital or clinic name")

class DoctorLogin(BaseModel):
    doctor_id: str = Field(..., description="8-digit doctor ID")
    password: str = Field(..., description="Password")

class DoctorResponse(BaseModel):
    id: int
    doctor_id: str
    full_name: str
    specialization: str
    hospital: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PatientOverview(BaseModel):
    user_id: int
    patient_id: str
    full_name: str
    age: int
    gender: str
    last_health_update: Optional[datetime]
    chronic_conditions: List[str]
    current_progress: Optional[int]
    progress_color: Optional[str]
    needs_attention: bool

class DoctorDashboard(BaseModel):
    doctor: DoctorResponse
    patients: List[PatientOverview]
    total_patients: int
    patients_needing_attention: int
    recent_insights: List[Dict[str, Any]]