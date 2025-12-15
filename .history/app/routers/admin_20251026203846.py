from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets
from app.database import get_db
from app.auth.security import get_password_hash
from app.auth.hashing import verify_password
from app.models.caregiver import Doctor

router = APIRouter(prefix="/admin", tags=["admin"])

# In a real application, you would have proper admin authentication
# For now, we'll use a simple superuser check

SUPERUSER_PASSWORD = "admin123"  # Change this in production

def verify_superuser(password: str):
    return password == SUPERUSER_PASSWORD

@router.post("/create-doctor")
async def create_doctor(
    doctor_data: dict,
    superuser_password: str,
    db: Session = Depends(get_db)
):
    if not verify_superuser(superuser_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superuser credentials"
        )
    
    # Check if doctor ID already exists
    existing_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_data["doctor_id"]).first()
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID already exists"
        )
    
    # Generate initial password (doctor will change it later)
    initial_password = secrets.token_urlsafe(8)
    hashed_password = get_password_hash(initial_password)
    
    doctor = Doctor(
        doctor_id=doctor_data["doctor_id"],
        hashed_password=hashed_password,
        full_name=doctor_data["full_name"],
        specialization=doctor_data["specialization"],
        hospital=doctor_data["hospital"],
        created_by="superuser"  # In real app, track which admin created this
    )
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    return {
        "message": "Doctor created successfully",
        "doctor_id": doctor.doctor_id,
        "initial_password": initial_password,  # Send this securely to the doctor
        "full_name": doctor.full_name,
        "specialization": doctor.specialization
    }

@router.get("/doctors")
async def list_doctors(
    superuser_password: str,
    db: Session = Depends(get_db)
):
    if not verify_superuser(superuser_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superuser credentials"
        )
    
    doctors = db.query(Doctor).all()
    return {
        "doctors": [
            {
                "doctor_id": doctor.doctor_id,
                "full_name": doctor.full_name,
                "specialization": doctor.specialization,
                "hospital": doctor.hospital,
                "is_active": doctor.is_active,
                "created_at": doctor.created_at
            }
            for doctor in doctors
        ]
    }