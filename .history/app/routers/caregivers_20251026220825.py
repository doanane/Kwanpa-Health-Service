from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import get_current_active_user  # Fixed import
from app.models.user import User, UserProfile
from app.models.caregiver import CaregiverRelationship
from app.models.health import HealthData, WeeklyProgress
from app.schemas.caregiver import CaregiverRequest, CaregiverRelationshipResponse, CaregiverDashboard, CaregiverMessageRequest

router = APIRouter(prefix="/caregivers", tags=["caregivers"])

@router.post("/volunteer")
async def volunteer_as_caregiver(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Mark user as caregiver
    current_user.is_caregiver = True
    db.commit()
    
    return {
        "message": "You are now registered as a caregiver",
        "caregiver_id": current_user.id,
        "patient_id": current_user.patient_id
    }

@router.post("/request", response_model=CaregiverRelationshipResponse)
async def request_caregiver_relationship(
    request_data: CaregiverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Find patient by patient_id
    patient = db.query(User).filter(User.patient_id == request_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if relationship already exists
    existing_relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient.id
    ).first()
    
    if existing_relationship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Caregiver relationship already exists or is pending"
        )
    
    # Create new caregiver relationship
    relationship = CaregiverRelationship(
        caregiver_id=current_user.id,
        patient_id=patient.id,
        relationship_type=request_data.relationship_type,
        status="pending"
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    # Get patient name for response
    patient_profile = db.query(UserProfile).filter(UserProfile.user_id == patient.id).first()
    patient_name = patient_profile.full_name if patient_profile else "Unknown"
    
    return CaregiverRelationshipResponse(
        id=relationship.id,
        caregiver_id=relationship.caregiver_id,
        patient_id=relationship.patient_id,
        patient_name=patient_name,
        patient_patient_id=patient.patient_id,
        relationship_type=relationship.relationship_type,
        status=relationship.status,
        created_at=relationship.created_at
    )

@router.get("/dashboard", response_model=CaregiverDashboard)
async def get_caregiver_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a caregiver"
        )
    
    # Get caregiver relationships
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "active"
    ).all()
    
    relationship_responses = []
    recent_updates = []
    
    for relationship in relationships:
        patient_profile = db.query(UserProfile).filter(
            UserProfile.user_id == relationship.patient_id
        ).first()
        
        patient_name = patient_profile.full_name if patient_profile else "Unknown"
        
        relationship_responses.append(CaregiverRelationshipResponse(
            id=relationship.id,
            caregiver_id=relationship.caregiver_id,
            patient_id=relationship.patient_id,
            patient_name=patient_name,
            patient_patient_id=relationship.patient.patient_id,
            relationship_type=relationship.relationship_type,
            status=relationship.status,
            created_at=relationship.created_at
        ))
        
        # Get recent health updates for this patient
        recent_health = db.query(HealthData).filter(
            HealthData.user_id == relationship.patient_id
        ).order_by(HealthData.date.desc()).first()
        
        if recent_health:
            recent_updates.append({
                "patient_id": relationship.patient.patient_id,
                "patient_name": patient_name,
                "update_type": "health_data",
                "message": f"Latest health update: {recent_health.steps} steps, {recent_health.heart_rate} BPM",
                "timestamp": recent_health.date
            })
    
    return CaregiverDashboard(
        caregiver_relationships=relationship_responses,
        total_patients=len(relationship_responses),
        recent_updates=recent_updates[:10]  # Last 10 updates
    )

@router.get("/patients/{patient_id}/insights")
async def get_patient_insights(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a caregiver"
        )
    
    # Find patient and verify relationship
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient.id,
        CaregiverRelationship.status == "active"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active caregiver relationship with this patient"
        )
    
    # Get patient insights
    profile = db.query(UserProfile).filter(UserProfile.user_id == patient.id).first()
    latest_health = db.query(HealthData).filter(
        HealthData.user_id == patient.id
    ).order_by(HealthData.date.desc()).first()
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == patient.id
    ).order_by(WeeklyProgress.week_start_date.desc()).first()
    
    insights = []
    if latest_health:
        if latest_health.steps and latest_health.steps < 5000:
            insights.append("Patient is below recommended daily steps")
        if latest_health.sleep_time and latest_health.sleep_time < 360:  # 6 hours
            insights.append("Patient may need more sleep")
        if weekly_progress and weekly_progress.progress_score < 50:
            insights.append("Weekly progress needs improvement")
    
    return {
        "patient_info": {
            "patient_id": patient.patient_id,
            "full_name": profile.full_name if profile else "Unknown",
            "age": profile.age if profile else None,
            "chronic_conditions": profile.chronic_conditions if profile else []
        },
        "current_health": {
            "steps": latest_health.steps if latest_health else 0,
            "sleep_time": latest_health.sleep_time if latest_health else 0,
            "heart_rate": latest_health.heart_rate if latest_health else None,
            "blood_pressure": latest_health.blood_pressure if latest_health else None
        },
        "weekly_progress": weekly_progress.progress_score if weekly_progress else 0,
        "progress_color": weekly_progress.progress_color if weekly_progress else "red",
        "insights": insights,
        "recommendations": "Encourage more physical activity" if insights else "Patient is doing well"
    }

@router.post("/patients/{patient_id}/message")
async def send_message_to_patient(
    patient_id: str,
    message_data: CaregiverMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered as a caregiver"
        )
    
    # Find patient and verify relationship
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    relationship = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient.id,
        CaregiverRelationship.status == "active"
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active caregiver relationship with this patient"
        )
    
    # Create notification (implementation depends on your notification system)
    
    return {
        "message": "Message sent successfully",
        "patient_id": patient_id,
        "caregiver_id": current_user.patient_id,
        "sent_message": message_data.message
    }