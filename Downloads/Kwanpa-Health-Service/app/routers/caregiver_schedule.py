from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field

from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver_schedule import CaregiverSchedule, AppointmentStatus, AppointmentType
from app.models.caregiver import CaregiverRelationship

router = APIRouter(prefix="/caregiver/schedule", tags=["caregiver_schedule"])

# Pydantic Models
class AppointmentCreate(BaseModel):
    patient_id: int
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    appointment_type: AppointmentType = AppointmentType.CHECKUP
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    is_virtual: bool = False
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    doctor_id: Optional[int] = None
    other_caregivers: Optional[List[int]] = None
    participant_notes: Optional[str] = None
    send_reminder: bool = True
    reminder_minutes_before: int = 30
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    appointment_type: Optional[AppointmentType] = None
    status: Optional[AppointmentStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    is_virtual: Optional[bool] = None
    meeting_link: Optional[str] = None
    meeting_platform: Optional[str] = None
    doctor_id: Optional[int] = None
    other_caregivers: Optional[List[int]] = None
    participant_notes: Optional[str] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    caregiver_id: int
    patient_id: int
    patient_name: str
    patient_email: str
    title: str
    description: Optional[str]
    appointment_type: str
    status: str
    start_time: datetime
    end_time: datetime
    duration_minutes: Optional[int]
    location: Optional[str]
    is_virtual: bool
    meeting_link: Optional[str]
    meeting_platform: Optional[str]
    doctor_id: Optional[int]
    other_caregivers: List[int]
    participant_notes: Optional[str]
    notes: Optional[str]
    attachments: List[str]
    color: str
    created_at: datetime

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    # Verify patient relationship
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == appointment_data.patient_id,
        CaregiverRelationship.status == "approved"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to schedule appointments for this patient"
        )
    
    # Verify patient exists
    patient = db.query(User).filter(User.id == appointment_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Calculate duration
    duration_minutes = None
    if appointment_data.start_time and appointment_data.end_time:
        duration_minutes = int((appointment_data.end_time - appointment_data.start_time).total_seconds() / 60)
    
    # Create appointment
    appointment = CaregiverSchedule(
        caregiver_id=current_user.id,
        patient_id=appointment_data.patient_id,
        title=appointment_data.title,
        description=appointment_data.description,
        appointment_type=appointment_data.appointment_type,
        start_time=appointment_data.start_time,
        end_time=appointment_data.end_time,
        duration_minutes=duration_minutes,
        location=appointment_data.location,
        is_virtual=appointment_data.is_virtual,
        meeting_link=appointment_data.meeting_link,
        meeting_platform=appointment_data.meeting_platform,
        doctor_id=appointment_data.doctor_id,
        other_caregivers=appointment_data.other_caregivers or [],
        participant_notes=appointment_data.participant_notes,
        send_reminder=appointment_data.send_reminder,
        reminder_minutes_before=appointment_data.reminder_minutes_before,
        notes=appointment_data.notes
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    
    return AppointmentResponse(
        id=appointment.id,
        caregiver_id=appointment.caregiver_id,
        patient_id=appointment.patient_id,
        patient_name=patient.username or patient.email,
        patient_email=patient.email,
        title=appointment.title,
        description=appointment.description,
        appointment_type=appointment.appointment_type.value,
        status=appointment.status.value,
        start_time=appointment.start_time,
        end_time=appointment.end_time,
        duration_minutes=appointment.duration_minutes,
        location=appointment.location,
        is_virtual=appointment.is_virtual,
        meeting_link=appointment.meeting_link,
        meeting_platform=appointment.meeting_platform,
        doctor_id=appointment.doctor_id,
        other_caregivers=appointment.other_caregivers or [],
        participant_notes=appointment.participant_notes,
        notes=appointment.notes,
        attachments=appointment.attachments or [],
        color=appointment.get_color(),
        created_at=appointment.created_at
    )

@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    status: Optional[AppointmentStatus] = None,
    appointment_type: Optional[AppointmentType] = None,
    patient_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get appointments for caregiver"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    query = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == current_user.id
    )
    
    # Apply filters
    if status:
        query = query.filter(CaregiverSchedule.status == status)
    if appointment_type:
        query = query.filter(CaregiverSchedule.appointment_type == appointment_type)
    if patient_id:
        # Verify relationship
        relationship = db.query(CaregiverRelationship).filter(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.patient_id == patient_id,
            CaregiverRelationship.status == "approved"
        ).first()
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view appointments for this patient"
            )
        query = query.filter(CaregiverSchedule.patient_id == patient_id)
    
    if start_date:
        query = query.filter(CaregiverSchedule.start_time >= start_date)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(CaregiverSchedule.start_time <= end_datetime)
    
    appointments = query.order_by(CaregiverSchedule.start_time).all()
    
    return [
        AppointmentResponse(
            id=appointment.id,
            caregiver_id=appointment.caregiver_id,
            patient_id=appointment.patient_id,
            patient_name=appointment.patient.username if appointment.patient else "Unknown",
            patient_email=appointment.patient.email if appointment.patient else "",
            title=appointment.title,
            description=appointment.description,
            appointment_type=appointment.appointment_type.value,
            status=appointment.status.value,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            duration_minutes=appointment.duration_minutes,
            location=appointment.location,
            is_virtual=appointment.is_virtual,
            meeting_link=appointment.meeting_link,
            meeting_platform=appointment.meeting_platform,
            doctor_id=appointment.doctor_id,
            other_caregivers=appointment.other_caregivers or [],
            participant_notes=appointment.participant_notes,
            notes=appointment.notes,
            attachments=appointment.attachments or [],
            color=appointment.get_color(),
            created_at=appointment.created_at
        )
        for appointment in appointments
    ]

@router.get("/today")
async def get_todays_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's appointments"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == current_user.id,
        CaregiverSchedule.start_time.between(today_start, today_end)
    ).order_by(CaregiverSchedule.start_time).all()
    
    return [
        appointment.to_dict()
        for appointment in appointments
    ]

@router.get("/upcoming")
async def get_upcoming_appointments(
    days: int = Query(7, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming appointments"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    future_end = today_start + timedelta(days=days)
    
    appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == current_user.id,
        CaregiverSchedule.start_time.between(today_start, future_end),
        CaregiverSchedule.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
    ).order_by(CaregiverSchedule.start_time).all()
    
    return [
        appointment.to_dict()
        for appointment in appointments
    ]

@router.put("/{appointment_id}")
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    
    appointment = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.id == appointment_id,
        CaregiverSchedule.caregiver_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Update fields
    update_data = appointment_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    # Recalculate duration if times changed
    if appointment_data.start_time or appointment_data.end_time:
        if appointment.start_time and appointment.end_time:
            appointment.duration_minutes = int(
                (appointment.end_time - appointment.start_time).total_seconds() / 60
            )
    
    appointment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(appointment)
    
    return appointment.to_dict()

@router.post("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    
    appointment = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.id == appointment_id,
        CaregiverSchedule.caregiver_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    appointment.updated_at = datetime.utcnow()
    db.commit()
    
    return appointment.to_dict()

@router.post("/{appointment_id}/complete")
async def complete_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark appointment as completed"""
    
    appointment = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.id == appointment_id,
        CaregiverSchedule.caregiver_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    appointment.status = AppointmentStatus.COMPLETED
    appointment.updated_at = datetime.utcnow()
    db.commit()
    
    return appointment.to_dict()

@router.get("/calendar")
async def get_calendar_view(
    month: int = Query(None, description="Month (1-12)"),
    year: int = Query(None, description="Year"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar view for appointments"""
    
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    now = datetime.utcnow()
    if not month or not year:
        month = now.month
        year = now.year
    
    # Calculate month range
    import calendar
    _, last_day = calendar.monthrange(year, month)
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == current_user.id,
        CaregiverSchedule.start_time.between(month_start, month_end)
    ).order_by(CaregiverSchedule.start_time).all()
    
    # Group by day
    calendar_data = {}
    for appointment in appointments:
        day = appointment.start_time.date().isoformat()
        if day not in calendar_data:
            calendar_data[day] = []
        
        calendar_data[day].append(appointment.to_dict())
    
    return {
        "month": month,
        "year": year,
        "calendar_data": calendar_data,
        "total_appointments": len(appointments)
    }