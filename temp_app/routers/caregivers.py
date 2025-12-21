from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import get_current_active_user_or_admin_or_admin_or_admin_or_admin_or_admin
from app.models.user import User
from app.models.caregiver import CaregiverRelationship
from app.models.user import UserProfile
from app.models.health import HealthData

router = APIRouter(prefix="/caregivers", tags=["caregivers"])

@router.post("/volunteer")
async def volunteer_as_caregiver(
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    current_user.is_caregiver = True
    db.commit()
    
    return {
        "message": "Successfully registered as caregiver volunteer",
        "user_id": current_user.id,
        "is_caregiver": True
    }

@router.post("/request")
async def request_caregiver_relationship(
    patient_id: int,
    relationship_type: str,
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be registered as a caregiver first"
        )
    
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    existing = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caregiver relationship already exists or pending"
        )
    
    relationship = CaregiverRelationship(
        caregiver_id=current_user.id,
        patient_id=patient_id,
        relationship_type=relationship_type,
        status="pending"
    )
    
    db.add(relationship)
    db.commit()
    
    return {
        "message": "Caregiver request sent successfully",
        "relationship_id": relationship.id,
        "status": "pending"
    }

@router.get("/dashboard")
async def get_caregiver_dashboard(
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a caregiver"
        )
    
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "approved"
    ).all()
    
    patients = []
    for rel in relationships:
        patient = db.query(User).filter(User.id == rel.patient_id).first()
        if patient:
            profile = db.query(UserProfile).filter(UserProfile.user_id == patient.id).first()
            latest_health = db.query(HealthData).filter(
                HealthData.user_id == patient.id
            ).order_by(HealthData.date.desc()).first()
            
            patients.append({
                "patient_id": patient.id,
                "patient_name": profile.full_name if profile else "Unknown",
                "relationship_type": rel.relationship_type,
                "latest_heart_rate": latest_health.heart_rate if latest_health else None,
                "latest_blood_pressure": latest_health.blood_pressure if latest_health else None,
                "status": "Stable" if latest_health and latest_health.heart_rate and latest_health.heart_rate < 100 else "Monitor"
            })
    
    return {
        "caregiver_id": current_user.id,
        "total_patients": len(patients),
        "patients": patients
    }

@router.get("/patients/{patient_id}/insights")
async def get_patient_insights(
    patient_id: int,
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient_id,
        CaregiverRelationship.status == "approved"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this patient's data"
        )
    
    patient = db.query(User).filter(User.id == patient_id).first()
    profile = db.query(UserProfile).filter(UserProfile.user_id == patient_id).first()
    
    latest_health = db.query(HealthData).filter(
        HealthData.user_id == patient_id
    ).order_by(HealthData.date.desc()).first()
    
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    
    weekly_data = db.query(HealthData).filter(
        HealthData.user_id == patient_id,
        HealthData.date >= week_ago
    ).all()
    
    avg_heart_rate = None
    if weekly_data:
        heart_rates = [d.heart_rate for d in weekly_data if d.heart_rate]
        if heart_rates:
            avg_heart_rate = sum(heart_rates) / len(heart_rates)
    
    return {
        "patient_id": patient_id,
        "patient_name": profile.full_name if profile else "Unknown",
        "latest_health_data": {
            "heart_rate": latest_health.heart_rate if latest_health else None,
            "blood_pressure": latest_health.blood_pressure if latest_health else None,
            "blood_glucose": latest_health.blood_glucose if latest_health else None,
            "last_updated": latest_health.date if latest_health else None
        },
        "weekly_average_heart_rate": avg_heart_rate,
        "insights": "Patient shows stable vital signs. Continue monitoring daily.",
        "recommendations": [
            "Ensure patient takes medication on time",
            "Monitor blood sugar levels before meals",
            "Encourage 30 minutes of daily walking"
        ]
    }

@router.post("/patients/{patient_id}/message")
async def send_message_to_patient(
    patient_id: int,
    message: str,
    db: Session = Depends(get_db),
    current: Union[User, Admin] = Depends(get_current_active_user_or_admin)
):
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient_id,
        CaregiverRelationship.status == "approved"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send messages to this patient"
        )
    
    from app.models.notification import Notification
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    caregiver_name = profile.full_name if profile else "Caregiver"
    
    notification = Notification(
        user_id=patient_id,
        notification_type="caregiver",
        title=f"Message from {caregiver_name}",
        message=message,
        sender_id=current_user.id,
        sender_type="caregiver"
    )
    
    db.add(notification)
    db.commit()
    
    return {"message": "Message sent successfully", "notification_id": notification.id}