from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class DoctorLogin(BaseModel):
    doctor_id: str = Field(..., min_length=8, max_length=8, description="8-digit doctor ID")
    password: str = Field(..., description="Password")

class DoctorProfileResponse(BaseModel):
    doctor_id: str
    full_name: str
    specialization: str
    hospital: str
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class PatientBasicInfo(BaseModel):
    patient_id: int
    full_name: str
    age: int
    gender: str
    chronic_conditions: List[str]

class AlertInfo(BaseModel):
    type: str
    message: str
    severity: str
    patient_name: str

class AppointmentInfo(BaseModel):
    patient_name: str
    appointment_time: datetime
    reason: str

class DoctorDashboardResponse(BaseModel):
    total_patients: int
    recent_alerts: List[AlertInfo]
    upcoming_appointments: List[AppointmentInfo]
    patients: List[PatientBasicInfo]

class PatientDashboardResponse(BaseModel):
    patient_info: Dict[str, Any]
    current_vitals: Dict[str, Any]
    health_metrics: Dict[str, Any]
    weekly_progress: Dict[str, Any]
    recent_food_analysis: List[Dict[str, Any]]
    medical_insights: List[str]