from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import create_access_token, get_current_active_doctor  # Fixed import
from app.auth.hashing import verify_password
from app.models.caregiver import Doctor
from app.models.user import User, UserProfile
from app.models.health import HealthData, WeeklyProgress, HealthInsight, FoodLog
from app.schemas.doctor import DoctorLogin, DoctorResponse, PatientOverview, DoctorDashboard
from app.schemas.user import Token
from app.schemas.health import HealthDataResponse
from app.schemas.caregiver import CaregiverMessageRequest

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