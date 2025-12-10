from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class CaregiverVolunteerRequest(BaseModel):
    experience: Optional[str] = Field(None, description="Previous caregiving experience")
    availability: Optional[str] = Field(None, description="Availability schedule")

class CaregiverRequestCreate(BaseModel):
    patient_id: int = Field(..., description="ID of patient to care for")
    relationship_type: str = Field(..., description="Relationship (family, friend, professional)")
    message: Optional[str] = Field(None, description="Optional message to patient")

class CaregiverDashboardResponse(BaseModel):
    caregiver_id: int
    total_patients: int
    patients: List[Dict[str, Any]]

class PatientInsightsResponse(BaseModel):
    patient_id: int
    patient_name: str
    latest_health_data: Dict[str, Any]
    weekly_average_heart_rate: Optional[float]
    insights: str
    recommendations: List[str]