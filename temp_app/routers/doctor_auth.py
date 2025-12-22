from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from app.database import get_db
from app.auth.security import create_access_token, verify_password, get_password_hash
from app.models.caregiver import Doctor
from app.models.user import UserSession
from app.services.email_service import email_service
from app.config import settings
from pydantic import BaseModel, EmailStr, Field
import uuid

router = APIRouter(prefix="/doctors/auth", tags=["doctor_authentication"])

# Pydantic Models
class DoctorLogin(BaseModel):
    doctor_id: str = Field(..., min_length=8, max_length=8)
    password: str

class DoctorChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class DoctorResetPassword(BaseModel):
    doctor_id: str
    new_password: str = Field(..., min_length=8)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: str
    doctor_id: str
    full_name: str
    specialization: str
    is_active: bool

# Helper Functions
def generate_token(length=32):
    """Generate random token"""
    return secrets.token_urlsafe(length)

def create_doctor_session(doctor_id: int, request: Request, db: Session):
    """Create doctor session"""
    session_token = generate_token()
    device_info = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    
    session = UserSession(
        user_id=doctor_id,  # Note: Using user_id field for doctor sessions
        session_token=session_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(session)
    db.commit()
    return session_token

# Endpoints
@router.post("/login", response_model=TokenResponse)
async def doctor_login(
    login_data: DoctorLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Doctor login with doctor_id and password"""
    doctor = db.query(Doctor).filter(Doctor.doctor_id == login_data.doctor_id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor ID or password"
        )
    
    if not verify_password(login_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid doctor ID or password"
        )
    
    if not doctor.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor account is inactive"
        )
    
    # Check if this is first login (no email set or using default password)
    is_first_login = not doctor.email or doctor.created_by == "system"
    
    # If first login, doctor must set email and change password
    if is_first_login:
        return {
            "message": "First login detected. Please set your email and change password.",
            "requires_setup": True,
            "doctor_id": doctor.doctor_id
        }
    
    # Create access token
    access_token = create_access_token(
        data={"sub": doctor.doctor_id},
        user_type="doctor"
    )
    
    # Create session
    create_doctor_session(doctor.id, request, db)
    
    return TokenResponse(
        access_token=access_token,
        user_type="doctor",
        doctor_id=doctor.doctor_id,
        full_name=doctor.full_name,
        specialization=doctor.specialization,
        is_active=doctor.is_active
    )

@router.post("/first-login-setup")
async def doctor_first_login_setup(
    doctor_id: str,
    email: EmailStr,
    new_password: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Doctor first login setup (set email and change password)"""
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check if email already used
    existing_doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if existing_doctor and existing_doctor.id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Update doctor info
    doctor.email = email
    doctor.hashed_password = get_password_hash(new_password)
    
    db.commit()
    
    # Send welcome email
    email_service.send_email(
        email,
        "Welcome to HEWAL3 Doctor Portal",
        f"""
        <h1>Welcome Dr. {doctor.full_name}!</h1>
        <p>Your HEWAL3 Doctor Portal account has been activated.</p>
        <p><strong>Doctor ID:</strong> {doctor.doctor_id}</p>
        <p><strong>Specialization:</strong> {doctor.specialization}</p>
        <p><strong>Hospital:</strong> {doctor.hospital}</p>
        <p>You can now access the doctor dashboard to monitor your patients.</p>
        <p>Login at: http://localhost:3000/doctor/login</p>
        """
    )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": doctor.doctor_id},
        user_type="doctor"
    )
    
    # Create session
    create_doctor_session(doctor.id, request, db)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "doctor",
        "doctor_id": doctor.doctor_id,
        "full_name": doctor.full_name,
        "message": "Setup completed successfully"
    }

@router.post("/change-password")
async def doctor_change_password(
    request_data: DoctorChangePassword,
    current_doctor: Doctor = Depends(get_current_active_doctor),
    db: Session = Depends(get_db)
):
    """Doctor change password"""
    if not verify_password(request_data.current_password, current_doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_doctor.hashed_password = get_password_hash(request_data.new_password)
    db.commit()
    
    # Send notification email
    if current_doctor.email:
        email_service.send_email(
            current_doctor.email,
            "Password Changed - HEWAL3 Doctor Portal",
            f"""
            <h2>Password Changed Successfully</h2>
            <p>Your HEWAL3 Doctor Portal password was changed on {datetime.now().strftime('%Y-%m-%d %H:%M')}.</p>
            <p>If you didn't make this change, please contact HEWAL3 support immediately.</p>
            """
        )
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def doctor_forgot_password(
    doctor_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Doctor forgot password (admin reset required)"""
    doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    
    if not doctor or not doctor.email:
        # For security, don't reveal if doctor exists
        return {"message": "If a doctor with this ID exists and has email registered, admin will be notified"}
    
    # In real implementation, this would notify admin to reset password
    # For now, we'll send email to doctor (in production, this should go to admin)
    background_tasks.add_task(
        email_service.send_email,
        doctor.email,
        "Password Reset Request - HEWAL3",
        f"""
        <h2>Password Reset Request</h2>
        <p>A password reset was requested for Doctor ID: {doctor.doctor_id}</p>
        <p><strong>Doctor:</strong> {doctor.full_name}</p>
        <p><strong>Specialization:</strong> {doctor.specialization}</p>
        <p>Please contact your system administrator to reset your password.</p>
        <p>Or visit: http://localhost:3000/doctor/reset-password/{doctor.doctor_id}</p>
        """
    )
    
    return {"message": "Password reset request submitted"}

@router.post("/logout")
async def doctor_logout(
    current_doctor: Doctor = Depends(get_current_active_doctor),
    db: Session = Depends(get_db)
):
    """Doctor logout"""
    # Mark doctor's sessions as inactive
    db.query(UserSession).filter(UserSession.user_id == current_doctor.id).update({"is_active": False})
    db.commit()
    
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_doctor_info(
    current_doctor: Doctor = Depends(get_current_active_doctor)
):
    """Get current doctor information"""
    return {
        "doctor_id": current_doctor.doctor_id,
        "full_name": current_doctor.full_name,
        "specialization": current_doctor.specialization,
        "hospital": current_doctor.hospital,
        "email": current_doctor.email,
        "is_active": current_doctor.is_active,
        "created_by": current_doctor.created_by,
        "created_at": current_doctor.created_at,
        "patient_count": len(current_doctor.patients) if current_doctor.patients else 0
    }

@router.get("/dashboard")
async def doctor_dashboard(
    current_doctor: Doctor = Depends(get_current_active_doctor),
    db: Session = Depends(get_db)
):
    """Doctor dashboard with patient statistics"""
    from app.models.user import UserProfile
    
    # Get doctor's patients
    patients = db.query(UserProfile).filter(
        UserProfile.doctor_id == current_doctor.doctor_id,
        UserProfile.profile_completed == True
    ).all()
    
    # Calculate statistics
    total_patients = len(patients)
    
    # Get critical patients (mock logic - in real app, check vitals)
    from app.models.health import HealthData
    critical_patients = []
    
    for patient in patients[:5]:  # Check first 5 patients
        latest_health = db.query(HealthData).filter(
            HealthData.user_id == patient.user_id
        ).order_by(HealthData.date.desc()).first()
        
        if latest_health and latest_health.heart_rate and latest_health.heart_rate > 120:
            critical_patients.append({
                "patient_id": patient.user_id,
                "name": patient.full_name,
                "heart_rate": latest_health.heart_rate,
                "status": "critical"
            })
    
    # Recent appointments (mock data)
    recent_appointments = [
        {
            "patient_name": "John Doe",
            "appointment_time": "2025-12-10 10:00",
            "reason": "Routine checkup"
        },
        {
            "patient_name": "Jane Smith", 
            "appointment_time": "2025-12-10 14:30",
            "reason": "Blood pressure follow-up"
        }
    ]
    
    return {
        "doctor_info": {
            "doctor_id": current_doctor.doctor_id,
            "full_name": current_doctor.full_name,
            "specialization": current_doctor.specialization
        },
        "statistics": {
            "total_patients": total_patients,
            "critical_patients": len(critical_patients),
            "stable_patients": total_patients - len(critical_patients),
            "new_patients_week": 3  # Mock data
        },
        "critical_patients": critical_patients[:3],
        "recent_appointments": recent_appointments,
        "quick_actions": [
            {"action": "view_patients", "label": "View All Patients", "endpoint": "/doctors/patients"},
            {"action": "add_patient", "label": "Add New Patient", "endpoint": "/doctors/patients/add"},
            {"action": "schedule_appointment", "label": "Schedule Appointment", "endpoint": "/doctors/appointments/schedule"}
        ]
    }