from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DashboardStats(BaseModel):
    total_patients: int = 0
    active_patients: int = 0
    critical_patients: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    overdue_tasks: int = 0
    todays_appointments: int = 0
    weekly_appointments: int = 0
    avg_health_score: int = 0

class PatientOverview(BaseModel):
    id: int
    name: str
    email: str
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    status: str
    health_score: Optional[int] = None
    last_checkup: Optional[datetime] = None
    next_appointment: Optional[datetime] = None
    conditions: List[str] = []
    recent_vitals: Optional[Dict[str, Any]] = None

class TaskOverview(BaseModel):
    id: int
    title: str
    patient_id: int
    patient_name: str
    task_type: str
    status: str
    priority: str
    due_date: Optional[datetime] = None
    is_overdue: bool = False

class AppointmentOverview(BaseModel):
    id: int
    title: str
    patient_id: int
    patient_name: str
    appointment_type: str
    status: str
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_virtual: bool = False

class VitalTrend(BaseModel):
    metric: str
    current_value: float
    unit: str
    trend: str 
    change_percentage: float
    last_updated: datetime

class AlertItem(BaseModel):
    id: int
    type: str 
    title: str
    message: str
    patient_id: int
    patient_name: str
    timestamp: datetime
    is_read: bool = False

class CaregiverDashboardResponse(BaseModel):
    stats: DashboardStats
    recent_patients: List[PatientOverview]
    upcoming_tasks: List[TaskOverview]
    todays_appointments: List[AppointmentOverview]
    recent_alerts: List[AlertItem]
    vital_trends: List[VitalTrend]
    caregiver_info: Dict[str, Any]
    last_updated: datetime