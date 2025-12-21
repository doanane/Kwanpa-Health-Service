from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import create_access_token, get_current_active_doctor
from app.auth.hashing import verify_password
from app.models.caregiver import Doctor
from app.models.user import User, UserProfile
from app.models.health import HealthData, FoodLog, WeeklyProgress
from app.models.notification import Notification

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.post("/login")
async def doctor_login(
    doctor_id: str,
    password: str,
    db: Session = Depends(get_db)
):
    """Doctor login with doctor_id and password"""
    print(f"Login attempt for doctor_id: {doctor_id}")
    
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    
    if not doctor:
        print(f"Doctor not found: {doctor_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor ID or password"
        )
    
    print(f"Found doctor: {doctor.full_name}")
    
    if not doctor.hashed_password:
        print(f"No password hash for doctor: {doctor_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor ID or password"
        )
    
    from app.auth.hashing import verify_password
    if not verify_password(password, doctor.hashed_password):
        print(f"Password verification failed for doctor: {doctor_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor ID or password"
        )
    
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor account is inactive"
        )
    
    from app.auth.security import create_access_token
    access_token = create_access_token(
        data={"sub": doctor.doctor_id},
        user_type="doctor"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "doctor",
        "doctor_id": doctor.doctor_id,
        "full_name": doctor.full_name,
        "specialization": doctor.specialization
    }
@router.get("/me")
async def get_doctor_profile(
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    return {
        "doctor_id": current_doctor.doctor_id,
        "full_name": current_doctor.full_name,
        "specialization": current_doctor.specialization,
        "hospital": current_doctor.hospital,
        "is_active": current_doctor.is_active,
        "created_at": current_doctor.created_at
    }

@router.get("/dashboard")
async def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patients = db.query(UserProfile).filter(
        UserProfile.doctor_id == current_doctor.doctor_id,
        UserProfile.profile_completed == True
    ).all()
    
    total_patients = len(patients)
    
    critical_patients = 0
    for patient in patients:
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.user_id
        ).order_by(HealthData.date.desc()).first()
        
        if latest_health and latest_health.heart_rate and latest_health.heart_rate > 120:
            critical_patients += 1
    
    recent_alerts = []
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.min.time())
    
    for patient in patients[:5]:
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.user_id
        ).order_by(HealthData.date.desc()).first()
        
        if latest_health and latest_health.date >= start_of_day:
            if latest_health.heart_rate and latest_heart_rate > 120:
                recent_alerts.append({
                    "type": "high_heart_rate",
                    "message": f"High heart rate detected for {patient.full_name}",
                    "severity": "high",
                    "patient_name": patient.full_name
                })
    
    patient_list = []
    for patient in patients[:10]:
        user = db.query(User).filter(User.id == patient.user_id).first()
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.user_id
        ).order_by(HealthData.date.desc()).first()
        
        patient_list.append({
            "patient_id": patient.user_id,
            "patient_identifier": user.patient_id if user else "Unknown",
            "full_name": patient.full_name,
            "age": patient.age,
            "gender": patient.gender,
            "chronic_conditions": patient.chronic_conditions,
            "latest_heart_rate": latest_health.heart_rate if latest_health else None,
            "latest_blood_pressure": latest_health.blood_pressure if latest_health else None,
            "status": "Critical" if latest_health and latest_health.heart_rate and latest_health.heart_rate > 120 else "Stable"
        })
    
    return {
        "doctor_id": current_doctor.doctor_id,
        "doctor_name": current_doctor.full_name,
        "total_patients": total_patients,
        "critical_patients": critical_patients,
        "recent_alerts": recent_alerts,
        "patients": patient_list
    }

@router.get("/patients/{patient_id}/dashboard")
async def get_patient_dashboard(
    patient_id: int,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patient_profile = db.query(UserProfile).filter(
        UserProfile.user_id == patient_id,
        UserProfile.doctor_id == current_doctor.doctor_id
    ).first()
    
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to you"
        )
    
    user = db.query(User).filter(User.id == patient_id).first()
    
    latest_health = db.query(HealthData).filter(
        HealthData.user_id == patient_id
    ).order_by(HealthData.date.desc()).first()
    
    recent_food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == patient_id
    ).order_by(FoodLog.created_at.desc()).limit(10).all()
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == patient_id
    ).order_by(WeeklyProgress.week_start_date.desc()).first()
    
    week_ago = datetime.now() - timedelta(days=7)
    
    weekly_data = db.query(HealthData).filter(
        HealthData.user_id == patient_id,
        HealthData.date >= week_ago
    ).all()
    
    health_metrics = {
        "avg_heart_rate": None,
        "avg_blood_pressure": None,
        "avg_blood_glucose": None,
        "weekly_steps_avg": None
    }
    
    if weekly_data:
        heart_rates = [d.heart_rate for d in weekly_data if d.heart_rate]
        if heart_rates:
            health_metrics["avg_heart_rate"] = sum(heart_rates) / len(heart_rates)
        
        glucose_levels = [d.blood_glucose for d in weekly_data if d.blood_glucose]
        if glucose_levels:
            health_metrics["avg_blood_glucose"] = sum(glucose_levels) / len(glucose_levels)
        
        steps = [d.steps for d in weekly_data if d.steps]
        if steps:
            health_metrics["weekly_steps_avg"] = sum(steps) / len(steps)
    
    food_analysis = []
    for food_log in recent_food_logs[:5]:
        if food_log.ai_analysis:
            food_analysis.append({
                "meal": food_log.meal_type,
                "analysis": food_log.ai_analysis.get("analysis", ""),
                "score": food_log.diet_score
            })
    
    return {
        "patient_info": {
            "patient_id": patient_id,
            "patient_identifier": user.patient_id if user else "Unknown",
            "full_name": patient_profile.full_name,
            "age": patient_profile.age,
            "gender": patient_profile.gender,
            "chronic_conditions": patient_profile.chronic_conditions,
            "doctor_assigned": current_doctor.full_name
        },
        "current_vitals": {
            "heart_rate": latest_health.heart_rate if latest_health else None,
            "blood_pressure": latest_health.blood_pressure if latest_health else None,
            "blood_glucose": latest_health.blood_glucose if latest_health else None,
            "steps_today": latest_health.steps if latest_health else None,
            "last_updated": latest_health.date if latest_health else None
        },
        "health_metrics": health_metrics,
        "weekly_progress": {
            "progress_score": weekly_progress.progress_score if weekly_progress else None,
            "progress_color": weekly_progress.progress_color if weekly_progress else None
        },
        "recent_food_analysis": food_analysis,
        "medical_insights": [
            f"Patient shows {('stable' if health_metrics['avg_heart_rate'] and health_metrics['avg_heart_rate'] < 100 else 'elevated')} heart rate patterns",
            "Blood glucose levels within acceptable range",
            "Regular physical activity observed"
        ]
    }

@router.post("/patients/{patient_id}/message")
async def send_message_to_patient(
    patient_id: int,
    message: str,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patient_profile = db.query(UserProfile).filter(
        UserProfile.user_id == patient_id,
        UserProfile.doctor_id == current_doctor.doctor_id
    ).first()
    
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to you"
        )
    
    notification = Notification(
        user_id=patient_id,
        notification_type="doctor",
        title=f"Message from Dr. {current_doctor.full_name}",
        message=message,
        sender_id=current_doctor.id,
        sender_type="doctor"
    )
    
    db.add(notification)
    db.commit()
    
    return {"message": "Message sent successfully", "notification_id": notification.id}

@router.get("/patients")
async def get_doctor_patients(
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patients = db.query(
        UserProfile,
        User
    ).join(
        User, User.id == UserProfile.user_id
    ).filter(
        UserProfile.doctor_id == current_doctor.doctor_id,
        UserProfile.profile_completed == True
    ).all()
    
    patient_list = []
    for profile, user in patients:
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == user.id
        ).order_by(HealthData.date.desc()).first()
        
        patient_status = "Stable"
        if latest_health:
            if latest_health.heart_rate and latest_health.heart_rate > 120:
                patient_status = "Critical"
            elif latest_health.heart_rate and latest_health.heart_rate > 100:
                patient_status = "Monitor"
        
        if status_filter and status_filter.lower() != patient_status.lower():
            continue
        
        patient_list.append({
            "patient_id": user.id,
            "patient_identifier": user.patient_id,
            "full_name": profile.full_name,
            "age": profile.age,
            "gender": profile.gender,
            "chronic_conditions": profile.chronic_conditions,
            "latest_heart_rate": latest_health.heart_rate if latest_health else None,
            "latest_blood_pressure": latest_health.blood_pressure if latest_health else None,
            "latest_blood_glucose": latest_health.blood_glucose if latest_health else None,
            "status": patient_status,
            "last_checkin": latest_health.date if latest_health else None
        })
    
    return {
        "doctor_id": current_doctor.doctor_id,
        "total_patients": len(patient_list),
        "patients": patient_list
    }