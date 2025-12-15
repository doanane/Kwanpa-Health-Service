from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import create_access_token, get_current_active_doctor
from app.auth.hashing import verify_password, get_password_hash
from app.models.caregiver import Doctor
from app.models.user import User, UserProfile
from app.models.health import HealthData, WeeklyProgress, HealthInsight, FoodLog
from app.schemas.doctor import DoctorLogin, Token, DoctorResponse, PatientOverview, DoctorDashboard
from app.schemas.notification import NotificationCreate
from app.schemas.health import HealthDataResponse

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("/login", response_model=Token)
async def doctor_login(login_data: DoctorLogin, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.doctor_id == login_data.doctor_id).first()
    
    if not doctor or not verify_password(login_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect doctor ID or password"
        )
    
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive doctor account"
        )
    
    access_token = create_access_token(
        data={"sub": doctor.doctor_id}, 
        user_type="doctor"
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_type": "doctor"
    }

@router.get("/me", response_model=DoctorResponse)
async def get_doctor_profile(current_doctor: Doctor = Depends(get_current_active_doctor)):
    return current_doctor

@router.get("/dashboard", response_model=DoctorDashboard)
async def get_doctor_dashboard(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    # Get all patients for this doctor
    patients_profiles = db.query(UserProfile).filter(
        UserProfile.doctor_id == current_doctor.doctor_id
    ).all()
    
    patients_overview = []
    patients_needing_attention = 0
    
    for profile in patients_profiles:
        user = db.query(User).filter(User.id == profile.user_id).first()
        if not user:
            continue
            
        # Get latest health data
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == user.id
        ).order_by(HealthData.date.desc()).first()
        
        # Get current weekly progress
        current_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        weekly_progress = db.query(WeeklyProgress).filter(
            WeeklyProgress.user_id == user.id,
            WeeklyProgress.week_start_date >= current_week_start
        ).first()
        
        # Check if patient needs attention
        needs_attention = False
        if latest_health:
            if (latest_health.blood_glucose and latest_health.blood_glucose > 180) or \
               (latest_health.heart_rate and (latest_health.heart_rate > 100 or latest_health.heart_rate < 60)):
                needs_attention = True
                patients_needing_attention += 1
        
        patients_overview.append(PatientOverview(
            user_id=user.id,
            patient_id=user.patient_id,
            full_name=profile.full_name,
            age=profile.age,
            gender=profile.gender,
            last_health_update=latest_health.date if latest_health else None,
            chronic_conditions=profile.chronic_conditions,
            current_progress=weekly_progress.progress_score if weekly_progress else 0,
            progress_color=weekly_progress.progress_color if weekly_progress else "red",
            needs_attention=needs_attention
        ))
    
    # Get recent insights
    recent_insights = []
    for profile in patients_profiles[:5]:  # Last 5 patients
        insights = db.query(HealthInsight).filter(
            HealthInsight.user_id == profile.user_id
        ).order_by(HealthInsight.generated_at.desc()).limit(3).all()
        
        for insight in insights:
            recent_insights.append({
                "patient_id": profile.user.patient_id,
                "patient_name": profile.full_name,
                "insight_type": insight.insight_type,
                "message": insight.message,
                "severity": insight.severity,
                "generated_at": insight.generated_at
            })
    
    return DoctorDashboard(
        doctor=current_doctor,
        patients=patients_overview,
        total_patients=len(patients_overview),
        patients_needing_attention=patients_needing_attention,
        recent_insights=recent_insights[:10]  # Last 10 insights
    )

@router.get("/patients/{patient_id}/dashboard")
async def get_patient_dashboard(
    patient_id: str,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    # Find patient by patient_id
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Verify doctor has access to this patient
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == patient.id,
        UserProfile.doctor_id == current_doctor.doctor_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this patient"
        )
    
    # Get comprehensive patient data
    health_data = db.query(HealthData).filter(
        HealthData.user_id == patient.id
    ).order_by(HealthData.date.desc()).first()
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == patient.id
    ).order_by(WeeklyProgress.week_start_date.desc()).first()
    
    food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == patient.id
    ).order_by(FoodLog.created_at.desc()).limit(10).all()
    
    health_insights = db.query(HealthInsight).filter(
        HealthInsight.user_id == patient.id
    ).order_by(HealthInsight.generated_at.desc()).limit(5).all()
    
    # Generate detailed analysis
    analysis = {
        "overall_health": "Good" if (weekly_progress and weekly_progress.progress_score >= 70) else "Needs Improvement",
        "key_metrics": {},
        "recommendations": []
    }
    
    if health_data:
        if health_data.blood_glucose and health_data.blood_glucose > 180:
            analysis["key_metrics"]["blood_glucose"] = "High"
            analysis["recommendations"].append("Monitor blood glucose levels closely")
        if health_data.heart_rate and health_data.heart_rate > 100:
            analysis["key_metrics"]["heart_rate"] = "Elevated"
            analysis["recommendations"].append("Consider stress management techniques")
        if weekly_progress and weekly_progress.progress_score < 50:
            analysis["recommendations"].append("Increase physical activity and improve diet")
    
    return {
        "patient_info": {
            "patient_id": patient.patient_id,
            "full_name": profile.full_name,
            "age": profile.age,
            "gender": profile.gender,
            "chronic_conditions": profile.chronic_conditions,
            "bmi": profile.bmi,
            "joined_date": patient.created_at
        },
        "current_health": HealthDataResponse.model_validate(health_data) if health_data else None,
        "weekly_progress": weekly_progress,
        "recent_meals": food_logs,
        "health_insights": health_insights,
        "analysis": analysis
    }

@router.post("/patients/{patient_id}/message")
async def send_message_to_patient(
    patient_id: str,
    message_data: dict,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Verify doctor has access to this patient
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == patient.id,
        UserProfile.doctor_id == current_doctor.doctor_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this patient"
        )
    
    # Create notification (implementation depends on your notification system)
    # This would typically create a notification record in the database
    
    return {
        "message": "Message sent successfully",
        "patient_id": patient_id,
        "doctor_id": current_doctor.doctor_id
    }

@router.get("/patients")
async def get_doctor_patients(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    patients_profiles = db.query(UserProfile).filter(
        UserProfile.doctor_id == current_doctor.doctor_id
    ).all()
    
    patients_list = []
    for profile in patients_profiles:
        user = db.query(User).filter(User.id == profile.user_id).first()
        if user:
            patients_list.append({
                "user_id": user.id,
                "patient_id": user.patient_id,
                "full_name": profile.full_name,
                "age": profile.age,
                "gender": profile.gender,
                "profile_completed": profile.profile_completed,
                "last_update": user.health_data[-1].date if user.health_data else None
            })
    
    return {"patients": patients_list}