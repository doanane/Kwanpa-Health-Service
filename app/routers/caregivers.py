from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User
from app.models.caregiver import CaregiverRelationship

router = APIRouter(prefix="/caregivers", tags=["caregivers"])


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
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    
    assignments = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "approved"
    ).all()
    
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
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    
    relationships = db.query(CaregiverRelationship).filter(
        CaregiverRelationship.caregiver_id == current_user.id,
        CaregiverRelationship.status == "approved"
    ).all()
    
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

@router.post("/request-access")
async def request_patient_access(
    request: AssignPatientRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request access to a patient as caregiver"""
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    
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
    if not getattr(current_user, 'is_caregiver', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
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
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only caregivers can connect with patients"
        )
    
    # Validate patient_caregiver_id input
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

@router.get("/my-id")
async def get_my_caregiver_id(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get caregiver's unique ID"""
    if not current_user.is_caregiver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a caregiver"
        )
    
    
    if not current_user.caregiver_id:
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
    
    return {
        "total_patients": len(patient_ids),
        "pending_requests": db.query(CaregiverRelationship).filter(
            CaregiverRelationship.caregiver_id == current_user.id,
            CaregiverRelationship.status == "pending"
        ).count(),
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