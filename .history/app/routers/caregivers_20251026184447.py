from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserProfile
from app.models.health import HealthData, WeeklyProgress, FoodLog
from app.models.notification import Notification

router = APIRouter(prefix="/caregivers", tags=["caregivers"])

@router.post("/doctor-login")
async def doctor_login(credentials: dict, db: Session = Depends(get_db)):
    doctor_id = credentials.get("doctor_id")
    password = credentials.get("password")
    
    if not doctor_id or not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # For demo, accept any doctor_id/password
    return {
        "access_token": f"doctor_token_{doctor_id}",
        "token_type": "bearer",
        "doctor_id": doctor_id
    }

@router.get("/patients")
async def get_patients(
    doctor_id: str,
    db: Session = Depends(get_db)
):
    # Get patients for this doctor
    patients = db.query(UserProfile).filter(
        UserProfile.doctor_id == doctor_id
    ).all()
    
    patient_data = []
    for patient in patients:
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.user_id
        ).order_by(HealthData.date.desc()).first()
        
        patient_data.append({
            "user_id": patient.user_id,
            "full_name": patient.full_name,
            "age": patient.age,
            "gender": patient.gender,
            "last_health_update": latest_health.date if latest_health else None,
            "chronic_conditions": patient.chronic_conditions
        })
    
    return {"patients": patient_data}

@router.get("/patient/{patient_id}/dashboard")
async def get_patient_dashboard(
    patient_id: int,
    doctor_id: str,
    db: Session = Depends(get_db)
):
    # Verify doctor has access to this patient
    patient_profile = db.query(UserProfile).filter(
        UserProfile.user_id == patient_id,
        UserProfile.doctor_id == doctor_id
    ).first()
    
    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or access denied"
        )
    
    # Get comprehensive patient data
    health_data = db.query(HealthData).filter(
        HealthData.user_id == patient_id
    ).order_by(HealthData.date.desc()).first()
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == patient_id
    ).order_by(WeeklyProgress.week_start_date.desc()).first()
    
    recent_food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == patient_id
    ).order_by(FoodLog.created_at.desc()).limit(5).all()
    
    # Generate insights
    insights = []
    if health_data:
        if health_data.blood_glucose and health_data.blood_glucose > 140:
            insights.append("Blood glucose levels are elevated")
        if health_data.heart_rate and health_data.heart_rate > 100:
            insights.append("Heart rate is higher than normal")
        if weekly_progress and weekly_progress.progress_score < 50:
            insights.append("Weekly progress needs improvement")
    
    return {
        "patient_info": {
            "full_name": patient_profile.full_name,
            "age": patient_profile.age,
            "gender": patient_profile.gender,
            "chronic_conditions": patient_profile.chronic_conditions
        },
        "current_health": health_data,
        "weekly_progress": weekly_progress,
        "recent_meals": recent_food_logs,
        "insights": insights,
        "recommendations": "Monitor blood glucose levels regularly" if insights else "Patient is doing well"
    }

@router.post("/send-message")
async def send_message(
    message_data: dict,
    db: Session = Depends(get_db)
):
    patient_id = message_data.get("patient_id")
    sender_id = message_data.get("sender_id")
    sender_type = message_data.get("sender_type", "caregiver")
    message = message_data.get("message")
    
    if not all([patient_id, sender_id, message]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields"
        )
    
    # Create notification
    notification = Notification(
        user_id=patient_id,
        notification_type=sender_type,
        title=f"Message from {sender_type}",
        message=message,
        sender_id=sender_id,
        sender_type=sender_type
    )
    
    db.add(notification)
    db.commit()
    
    return {"message": "Message sent successfully", "notification_id": notification.id}

@router.get("/ranking")
async def get_ranking(db: Session = Depends(get_db)):
    # Get users with their weekly progress for ranking
    weekly_progress = db.query(WeeklyProgress).order_by(
        WeeklyProgress.progress_score.desc()
    ).all()
    
    ranking_data = []
    for progress in weekly_progress:
        profile = db.query(UserProfile).filter(
            UserProfile.user_id == progress.user_id
        ).first()
        
        if profile:
            ranking_data.append({
                "user_id": progress.user_id,
                "unique_id": f"USER{progress.user_id:04d}",
                "progress_score": progress.progress_score,
                "progress_color": progress.progress_color
            })
    
    return {"ranking": ranking_data}