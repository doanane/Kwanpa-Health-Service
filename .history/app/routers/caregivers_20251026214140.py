from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.security import get_current_active_user
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
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/dashboard", response_model=CaregiverDashboard)
async def get_caregiver_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/patients/{patient_id}/insights")
async def get_patient_insights(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

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