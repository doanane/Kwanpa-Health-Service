from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CaregiverRequest(BaseModel):
    patient_id: str = Field(..., description="Patient ID to request caregiver relationship with")
    relationship_type: str = Field(..., description="Type of relationship (family, volunteer, professional)")

class CaregiverRelationshipResponse(BaseModel):
    id: int
    caregiver_id: int
    patient_id: int
    patient_name: str
    patient_patient_id: str
    relationship_type: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CaregiverDashboard(BaseModel):
    caregiver_relationships: List[CaregiverRelationshipResponse]
    total_patients: int
    recent_updates: List[Dict[str, Any]]

class CaregiverMessageRequest(BaseModel):
    message: str = Field(..., description="Message to send to patient")