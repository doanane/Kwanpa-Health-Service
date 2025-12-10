from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets
from app.database import get_db
from app.auth.hashing import get_password_hash
from app.auth.security import get_current_admin  
from app.models.caregiver import Doctor

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/create-doctor")
async def create_doctor(
    doctor_id: str,
    full_name: str,
    specialization: str,
    hospital: str,
    email: str = None,
    current_admin = Depends(get_current_admin),  # Change to get_current_admin
    db: Session = Depends(get_db)
):
    """Create a new doctor (requires admin JWT token)"""
    
    # Check if current admin is superadmin
    if not hasattr(current_admin, 'is_superadmin') or not current_admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmins can create doctors"
        )
    
    # Also check if admin is active
    if not current_admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    if len(doctor_id) != 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID must be 8 characters"
        )
    
    # Ensure doctor_id starts with DOC
    if not doctor_id.startswith("DOC"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID must start with 'DOC'"
        )
    
    existing_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID already exists"
        )
    
    initial_password = secrets.token_urlsafe(8)
    hashed_password = get_password_hash(initial_password)
    
    # Create doctor data dict
    doctor_data = {
        "doctor_id": doctor_id,
        "hashed_password": hashed_password,
        "full_name": full_name,
        "specialization": specialization,
        "hospital": hospital,
        "created_by": current_admin.email,
        "is_active": True
    }
    
    # Add email only if provided
    if email:
        doctor_data["email"] = email
    
    doctor = Doctor(**doctor_data)
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    return {
        "message": "Doctor created successfully",
        "doctor_id": doctor.doctor_id,
        "initial_password": initial_password,
        "full_name": doctor.full_name,
        "specialization": doctor.specialization,
        "hospital": doctor.hospital,
        "email": email,
        "created_by": current_admin.email,
        "note": "Doctor should change password on first login"
    }

@router.get("/doctors")
async def list_doctors(
    current_admin = Depends(get_current_admin),  # Change to get_current_admin
    db: Session = Depends(get_db)
):
    """List all doctors (requires admin JWT token)"""
    
    # Check if admin is active
    if not current_admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    doctors = db.query(Doctor).all()
    
    doctor_list = []
    for doctor in doctors:
        doctor_list.append({
            "doctor_id": doctor.doctor_id,
            "full_name": doctor.full_name,
            "specialization": doctor.specialization,
            "hospital": doctor.hospital,
            "email": doctor.email,
            "is_active": doctor.is_active,
            "created_at": doctor.created_at.isoformat() if doctor.created_at else None,
            "created_by": doctor.created_by
        })
    
    return {
        "total_doctors": len(doctor_list),
        "doctors": doctor_list
    }