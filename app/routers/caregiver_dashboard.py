from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, date
import logging

from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver import CaregiverRelationship
from app.models.health import HealthData
from app.models.caregiver_tasks import CaregiverTask, TaskStatus
from app.models.caregiver_schedule import CaregiverSchedule, AppointmentStatus
from app.schemas.caregiver_dashboard import (
    CaregiverDashboardResponse, DashboardStats, PatientOverview,
    TaskOverview, AppointmentOverview, AlertItem, VitalTrend
)

router = APIRouter(prefix="/caregivers", tags=["caregiver_dashboard"])
logger = logging.getLogger(__name__)

@router.get("/dashboard", response_model=CaregiverDashboardResponse)
async def get_caregiver_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "approved"
    ).all()
    
    patient_ids = [rel.patient_id for rel in relationships]
    patients = db.query(User).filter(User.id.in_(patient_ids)).all()
    
    stats = calculate_dashboard_stats(current_user.id, patient_ids, db)
    recent_patients = get_recent_patients(patients, db)
    upcoming_tasks = get_upcoming_tasks(current_user.id, db)
    todays_appointments = get_todays_appointments(current_user.id, db)
    recent_alerts = get_recent_alerts(patient_ids, db)
    vital_trends = get_vital_trends(patient_ids, db)
    
    caregiver_info = {
        "id": current_user.id,
        "name": f"{getattr(current_user, 'first_name', '')} {getattr(current_user, 'last_name', '')}".strip(),
        "email": current_user.email,
        "caregiver_id": getattr(current_user, 'caregiver_id', None),
        "phone": current_user.phone_number,
        "experience_years": getattr(current_user, 'experience_years', 0)
    }
    
    return CaregiverDashboardResponse(
        stats=stats,
        recent_patients=recent_patients,
        upcoming_tasks=upcoming_tasks,
        todays_appointments=todays_appointments,
        recent_alerts=recent_alerts,
        vital_trends=vital_trends,
        caregiver_info=caregiver_info,
        last_updated=datetime.utcnow()
    )

def calculate_dashboard_stats(caregiver_id: int, patient_ids: List[int], db: Session) -> DashboardStats:
    total_patients = len(patient_ids)
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_patients = db.query(HealthData.user_id).filter(
        HealthData.user_id.in_(patient_ids),
        HealthData.created_at >= week_ago
    ).distinct().count()
    
    critical_patients = 0
    
    pending_tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == caregiver_id,
        CaregiverTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).count()
    
    completed_tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == caregiver_id,
        CaregiverTask.status == TaskStatus.COMPLETED,
        CaregiverTask.completed_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    overdue_tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == caregiver_id,
        CaregiverTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
        CaregiverTask.due_date < datetime.utcnow()
    ).count()
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    todays_appointments_count = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == caregiver_id,
        CaregiverSchedule.start_time.between(today_start, today_end)
    ).count()
    
    week_end = today_end + timedelta(days=7)
    weekly_appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == caregiver_id,
        CaregiverSchedule.start_time.between(today_start, week_end)
    ).count()
    
    return DashboardStats(
        total_patients=total_patients,
        active_patients=active_patients,
        critical_patients=critical_patients,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks,
        todays_appointments=todays_appointments_count,
        weekly_appointments=weekly_appointments,
        avg_health_score=85
    )

def get_recent_patients(patients: List[User], db: Session) -> List[PatientOverview]:
    recent_patients = []
    
    for patient in patients[:5]:
        from app.models.user import UserProfile
        profile = db.query(UserProfile).filter(UserProfile.user_id == patient.id).first()
        
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.id
        ).order_by(HealthData.created_at.desc()).first()
        
        status = "stable"
        if latest_health:
            if getattr(latest_health, 'is_critical', False):
                status = "critical"
        
        recent_patients.append(PatientOverview(
            id=patient.id,
            name=profile.full_name if profile else patient.username or patient.email,
            email=patient.email,
            patient_id=patient.patient_id or f"PAT{patient.id:06d}",
            age=profile.age if profile else None,
            gender=profile.gender if profile else None,
            status=status,
            health_score=latest_health.health_score if latest_health else 0,
            last_checkup=latest_health.created_at if latest_health else None,
            conditions=profile.chronic_conditions if profile else [],
            recent_vitals={
                "heart_rate": latest_health.heart_rate if latest_health else None,
                "blood_pressure": latest_health.blood_pressure if latest_health else None,
                "blood_glucose": latest_health.blood_glucose if latest_health else None
            } if latest_health else None
        ))
    
    return recent_patients

def get_upcoming_tasks(caregiver_id: int, db: Session) -> List[TaskOverview]:
    tasks = db.query(CaregiverTask).filter(
        CaregiverTask.caregiver_id == caregiver_id,
        CaregiverTask.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).order_by(CaregiverTask.due_date).limit(10).all()
    
    return [
        TaskOverview(
            id=task.id,
            title=task.title,
            patient_id=task.patient_id,
            patient_name=task.patient.username if task.patient else "Unknown",
            task_type=task.task_type,
            status=task.status.value,
            priority=task.priority.value,
            due_date=task.due_date,
            is_overdue=task.is_overdue()
        )
        for task in tasks
    ]

def get_todays_appointments(caregiver_id: int, db: Session) -> List[AppointmentOverview]:
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    
    appointments = db.query(CaregiverSchedule).filter(
        CaregiverSchedule.caregiver_id == caregiver_id,
        CaregiverSchedule.start_time.between(today_start, today_end),
        CaregiverSchedule.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
    ).order_by(CaregiverSchedule.start_time).all()
    
    return [
        AppointmentOverview(
            id=appointment.id,
            title=appointment.title,
            patient_id=appointment.patient_id,
            patient_name=appointment.patient.username if appointment.patient else "Unknown",
            appointment_type=appointment.appointment_type.value,
            status=appointment.status.value,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            location=appointment.location,
            is_virtual=appointment.is_virtual
        )
        for appointment in appointments
    ]

def get_recent_alerts(patient_ids: List[int], db: Session) -> List[AlertItem]:
    from app.models.notification import Notification
    
    alerts = db.query(Notification).filter(
        Notification.user_id.in_(patient_ids),
        Notification.notification_type.in_(["critical", "warning"])
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return [
        AlertItem(
            id=notification.id,
            type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            patient_id=notification.user_id,
            patient_name=notification.user.username if notification.user else "Unknown",
            timestamp=notification.created_at,
            is_read=notification.is_read
        )
        for notification in alerts
    ]

def get_vital_trends(patient_ids: List[int], db: Session) -> List[VitalTrend]:
    trends = []
    week_ago = datetime.utcnow() - timedelta(days=7)
    heart_data = db.query(HealthData).filter(
        HealthData.user_id.in_(patient_ids),
        HealthData.heart_rate.isnot(None),
        HealthData.created_at >= week_ago
    ).all()
    
    if heart_data:
        avg_heart_rate = sum(d.heart_rate for d in heart_data if d.heart_rate) / len(heart_data)
        trends.append(VitalTrend(
            metric="Heart Rate",
            current_value=avg_heart_rate,
            unit="bpm",
            trend="stable",
            change_percentage=0.0,
            last_updated=datetime.utcnow()
        ))
    
    return trends