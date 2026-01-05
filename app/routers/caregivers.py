from fastapi import APIRouter, Depends, HTTPException, status, Body
import logging
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver import CaregiverRelationship
from app.models.notification import Notification
# Reuse messaging WebSocket manager for real-time signals when online
from app.routers.messages import manager as ws_manager

router = APIRouter(prefix="/caregivers", tags=["caregivers"])
logger = logging.getLogger(__name__)

# Pydantic Models
class CaregiverUpdateRequest(BaseModel):
    phone_number: Optional[str] = None

class AssignPatientRequest(BaseModel):
    patient_id: int
    relationship_type: str = "family"

class CaregiverProfileResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    phone_number: Optional[str]
    is_caregiver: bool
    assigned_patients_count: int
    created_at: datetime

class CaregiverPatientResponse(BaseModel):
    patient_id: int
    email: str
    username: Optional[str]
    phone_number: Optional[str]
    relationship_type: str
    status: str
    assigned_since: datetime

class IncomingRequestResponse(BaseModel):
    request_id: int
    caregiver_id: int
    caregiver_name: str
    caregiver_email: str
    relationship_type: str
    status: str
    created_at: datetime

class RespondRequestBody(BaseModel):
    action: str  # "approve" or "reject"

# Helper function to check if user is caregiver
def verify_caregiver(user: User) -> None:
    """Raise exception if user is not a caregiver"""
    if not getattr(user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires caregiver privileges"
        )

# Helper function to get approved relationships
def get_approved_relationships(user_id: int, db: Session) -> List[CaregiverRelationship]:
    """Get approved caregiver relationships for a user"""
    return db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == user_id,
        CaregiverRelationship.status == "approved"
    ).all()


def _create_notification(db: Session, user_id: int, title: str, message: str, sender_id: int, sender_type: str = "caregiver"):
    notification = Notification(
        user_id=user_id,
        notification_type="caregiver",
        title=title,
        message=message,
        sender_id=sender_id,
        sender_type=sender_type
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


async def _push_ws_event(user_id: int, payload: dict):
    try:
        await ws_manager.send_personal_message(payload, user_id)
    except Exception as e:
        # Non-fatal: user might be offline
        print(f"WS notify failed for user {user_id}: {e}")

# Endpoints
@router.get("/test")
async def test_endpoint():
    """Test if caregivers router is working"""
    return {"message": "Caregivers router is working!"}

@router.get("/profile", response_model=CaregiverProfileResponse)
async def get_caregiver_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get caregiver profile information"""
    verify_caregiver(current_user)
    
    assignments = get_approved_relationships(current_user.id, db)
    
    return {
        "id": current_user.id,
        "email": current_user.email or "",
        "username": getattr(current_user, 'username', None),
        "phone_number": getattr(current_user, 'phone_number', None),
        "is_caregiver": getattr(current_user, 'is_caregiver', False),
        "assigned_patients_count": len(assignments),
        "created_at": getattr(current_user, 'created_at', datetime.utcnow())
    }

@router.get("/patients", response_model=List[CaregiverPatientResponse])
async def get_assigned_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to this caregiver"""
    verify_caregiver(current_user)
    try:
        relationships = get_approved_relationships(current_user.id, db)
        patients = []
        for rel in relationships:
            patient = db.query(User).filter(User.id == rel.patient_id).first()
            if patient:
                patients.append({
                    "patient_id": patient.id,
                    "email": patient.email or "",
                    "username": getattr(patient, 'username', None),
                    "phone_number": getattr(patient, 'phone_number', None),
                    "relationship_type": rel.relationship_type,
                    "status": rel.status,
                    "assigned_since": rel.created_at
                })
        return patients
    except Exception:
        logger.exception("Error fetching assigned patients for caregiver_id=%s", getattr(current_user, "id", None))
        raise HTTPException(status_code=500, detail="Failed to fetch patients")

@router.post("/request-access")
async def request_patient_access(
    request: AssignPatientRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request access to a patient as caregiver"""
    verify_caregiver(current_user)
    
    patient = db.query(User).filter(User.id == request.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    existing = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == request.patient_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access request already exists"
        )
    
    relationship = CaregiverRelationship(
        caregiver_id=current_user.id,
        patient_id=request.patient_id,
        relationship_type=request.relationship_type,
        status="pending"
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    return {
        "message": "Access request sent successfully",
        "request_id": relationship.id,
        "status": relationship.status
    }

@router.put("/profile")
async def update_caregiver_profile(
    request: CaregiverUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update caregiver profile settings"""
    verify_caregiver(current_user)
    
    if request.phone_number is not None:
        current_user.phone_number = request.phone_number
        db.commit()
    
    return {"message": "Profile updated successfully"}

@router.post("/connect-patient")
async def connect_with_patient(
    patient_caregiver_id: str = Body(..., embed=True, description="Patient's Caregiver ID or Patient ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Connect with a patient using their ID"""
    verify_caregiver(current_user)
    
    if not patient_caregiver_id or not patient_caregiver_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient ID cannot be empty"
        )
    
    patient = db.query(User).filter(
        (User.caregiver_id == patient_caregiver_id) | 
        (User.patient_id == patient_caregiver_id)
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if patient.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot connect to yourself"
        )
    
    existing = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.patient_id == patient.id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Already connected with {patient.email}"
        )
    
    relationship = CaregiverRelationship(
        caregiver_id=current_user.id,
        patient_id=patient.id,
        relationship_type="professional",
        status="pending"
    )
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    
    return {
        "message": "Connection request sent to patient",
        "patient_email": patient.email,
        "patient_name": f"{getattr(patient, 'first_name', '')} {getattr(patient, 'last_name', '')}".strip(),
        "request_id": relationship.id,
        "status": relationship.status
    }


@router.post("/connect-caregiver")
async def connect_with_caregiver(
    caregiver_id: str = Body(..., embed=True, description="Caregiver ID to connect with"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Patient initiates a connection request to a caregiver using caregiver_id"""
    # Current user is patient by intent; no strict check to allow flexibility
    if not caregiver_id or not caregiver_id.strip():
        raise HTTPException(status_code=400, detail="Caregiver ID cannot be empty")

    caregiver = db.query(User).filter(User.caregiver_id == caregiver_id).first()
    if not caregiver:
        raise HTTPException(status_code=404, detail="Caregiver not found")

    if caregiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot connect to yourself")

    existing = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == caregiver.id,
        CaregiverRelationship.patient_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Request already exists or you are already connected")

    relationship = CaregiverRelationship(
        caregiver_id=caregiver.id,
        patient_id=current_user.id,
        relationship_type="professional",
        status="pending"
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    title = "New patient connection request"
    message = f"{current_user.email or current_user.username} wants to connect with you."
    _create_notification(db, caregiver.id, title, message, current_user.id, sender_type="patient")
    await _push_ws_event(caregiver.id, {"type": "connection_request", "request_id": relationship.id, "from_user_id": current_user.id})

    return {
        "message": "Connection request sent to caregiver",
        "caregiver_email": caregiver.email,
        "caregiver_name": f"{getattr(caregiver, 'first_name', '')} {getattr(caregiver, 'last_name', '')}".strip(),
        "request_id": relationship.id,
        "status": relationship.status
    }


@router.get("/requests/incoming", response_model=List[IncomingRequestResponse])
async def list_incoming_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Patients see pending caregiver connection requests"""
    requests = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.patient_id == current_user.id,
        CaregiverRelationship.status == "pending"
    ).order_by(CaregiverRelationship.created_at.desc()).all()

    result: List[IncomingRequestResponse] = []
    for rel in requests:
        caregiver = db.query(User).filter(User.id == rel.caregiver_id).first()
        if caregiver:
            result.append(IncomingRequestResponse(
                request_id=rel.id,
                caregiver_id=rel.caregiver_id,
                caregiver_name=f"{getattr(caregiver, 'first_name', '')} {getattr(caregiver, 'last_name', '')}".strip() or caregiver.email,
                caregiver_email=caregiver.email,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at
            ))

    return result


@router.post("/requests/{request_id}/respond")
async def respond_request(
    request_id: int,
    body: RespondRequestBody,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Patient approves or rejects a caregiver connection request"""
    rel = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.id == request_id,
        CaregiverRelationship.patient_id == current_user.id
    ).first()

    if not rel:
        raise HTTPException(status_code=404, detail="Request not found")

    if rel.status != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")

    action = body.action.lower()
    if action not in {"approve", "reject"}:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    rel.status = "approved" if action == "approve" else "rejected"
    db.commit()
    db.refresh(rel)

    caregiver = db.query(User).filter(User.id == rel.caregiver_id).first()
    title = "Connection response"
    message = f"Patient {current_user.email or current_user.username} {rel.status} your request."
    _create_notification(db, rel.caregiver_id, title, message, current_user.id, sender_type="patient")
    await _push_ws_event(rel.caregiver_id, {"type": "connection_response", "request_id": rel.id, "status": rel.status})

    return {"message": f"Request {rel.status}"}

@router.get("/my-id")
async def get_my_caregiver_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get caregiver's unique ID"""
    verify_caregiver(current_user)
    
    if not getattr(current_user, 'caregiver_id', None):
        current_user.caregiver_id = current_user.generate_caregiver_id()
        db.commit()
    
    return {
        "caregiver_id": current_user.caregiver_id,
        "name": f"{getattr(current_user, 'first_name', '')} {getattr(current_user, 'last_name', '')}".strip(),
        "email": current_user.email,
        "qr_code_url": f"/caregivers/qr/{current_user.caregiver_id}"
    }

@router.get("/dashboard")
async def caregiver_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get caregiver dashboard summary"""
    verify_caregiver(current_user)
    try:
        relationships = get_approved_relationships(current_user.id, db)
        patient_ids = [rel.patient_id for rel in relationships]
        pending_count = db.query(CaregiverRelationship).filter(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.status == "pending"
        ).count()
        return {
            "total_patients": len(patient_ids),
            "pending_requests": pending_count,
            "caregiver_status": "active",
            "recent_activity": [
                {
                    "patient_id": rel.patient_id,
                    "relationship_type": rel.relationship_type,
                    "status": rel.status,
                    "since": rel.created_at
                }
                for rel in relationships[:5]
            ]
        }
    except Exception:
        logger.exception("Error building caregiver dashboard for caregiver_id=%s", getattr(current_user, "id", None))
        raise HTTPException(status_code=500, detail="Failed to fetch caregiver dashboard")