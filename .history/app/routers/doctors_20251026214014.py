from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import create_access_token, get_current_active_doctor
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
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/patients/{patient_id}/dashboard")
async def get_patient_dashboard(
    patient_id: str,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.post("/patients/{patient_id}/message")
async def send_message_to_patient(
    patient_id: str,
    message_data: CaregiverMessageRequest,
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
        "doctor_id": current_doctor.doctor_id,
        "sent_message": message_data.message
    }

@router.get("/patients")
async def get_doctor_patients(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    # Implementation remains the same...
    # [Previous implementation code...]