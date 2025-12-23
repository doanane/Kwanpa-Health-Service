from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request

from app.schemas.caregiver_signup import CaregiverSignupRequest, CaregiverSignupResponse

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Query
import string
from typing import Optional, Union
import jwt
from app.database import get_db
from app.auth.security import create_access_token, verify_password, get_password_hash, get_current_user,    get_current_admin, get_current_user_or_admin,get_current_active_user_or_admin 
from app.auth.hashing import verify_password as verify_pass, get_password_hash as get_pass_hash
from app.models.user import User
from app.models.auth import PasswordResetToken, EmailVerificationToken, LoginOTP, RefreshToken, UserSession
from app.services.email_service import email_service
from app.services.sms_service import sms_service
from app.config import settings
from pydantic import BaseModel, EmailStr, Field, validator
import uuid
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from app.models.admin import Admin

router = APIRouter(prefix="/auth", tags=["authentication"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class VerifyEmailRequest(BaseModel):
    token: str

class RequestOTPLogin(BaseModel):
    email: EmailStr

class VerifyOTPLogin(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class CaregiverSignupRequest(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    caregiver_type: str = Field(..., description="family, friend, or professional")
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    agree_to_terms: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_type: str
    user_id: int
    email: str
    is_email_verified: bool


def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_token(length=32):
    """Generate random token"""
    return secrets.token_urlsafe(length)

def create_refresh_token(user_id: int, db: Session):
    """Create refresh token"""
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(refresh_token)
    db.commit()
    return token




    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1 class="error">Invalid or Expired Token</h1>
                <p>The password reset token is invalid or has expired.</p>
                <p>Please request a new password reset.</p>
                <p><a href="/docs#/authentication/forgot_password">Request New Password Reset</a></p>
            </body>
        </html>
        """)
    
    
    return HTMLResponse(content=f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 50px; max-width: 500px; margin: 0 auto; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input {{ width: 100%; padding: 10px; box-sizing: border-box; }}
                button {{ padding: 12px 24px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                .error {{ color: red; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>Set New Password</h1>
            <p>Please enter your new password.</p>
            <form id="resetForm">
                <input type="hidden" id="token" value="{token}">
                <div class="form-group">
                    <label for="password">New Password (min 8 characters):</label>
                    <input type="password" id="password" name="password" minlength="8" required>
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password:</label>
                    <input type="password" id="confirm_password" name="confirm_password" minlength="8" required>
                </div>
                <button type="submit">Reset Password</button>
            </form>
            <div id="message"></div>
            <script>
                document.getElementById('resetForm').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    const token = document.getElementById('token').value;
                    const password = document.getElementById('password').value;
                    const confirmPassword = document.getElementById('confirm_password').value;
                    
                    if (password !== confirmPassword) {{
                        document.getElementById('message').innerHTML = '<p class="error">Passwords do not match</p>';
                        return;
                    }}
                    
                    const response = await fetch('/auth/reset-password', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token, new_password: password }})
                    }});
                    
                    const result = await response.json();
                    const messageDiv = document.getElementById('message');
                    
                    if (response.ok) {{
                        messageDiv.innerHTML = '<p class="success">' + result.message + '</p>';
                        messageDiv.innerHTML += '<p>You can now <a href="/docs#/authentication/login">login</a> with your new password.</p>';
                    }} else {{
                        messageDiv.innerHTML = '<p class="error">' + (result.detail || 'Error resetting password') + '</p>';
                    }}
                }});
            </script>
        </body>
    </html>
    """)



    
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return """
        <html>
            <body>
                <h1 class="error">Invalid or Expired Token</h1>
                <p>The password reset token is invalid or has expired.</p>
                <p>Please request a new password reset.</p>
            </body>
        </html>
        """
    
    
    return f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 50px; max-width: 500px; margin: 0 auto; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input {{ width: 100%; padding: 10px; box-sizing: border-box; }}
                button {{ padding: 12px 24px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                .error {{ color: red; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>Set New Password</h1>
            <p>Please enter your new password.</p>
            <form id="resetForm">
                <input type="hidden" id="token" value="{token}">
                <div class="form-group">
                    <label for="password">New Password (min 8 characters):</label>
                    <input type="password" id="password" name="password" minlength="8" required>
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password:</label>
                    <input type="password" id="confirm_password" name="confirm_password" minlength="8" required>
                </div>
                <button type="submit">Reset Password</button>
            </form>
            <div id="message"></div>
            <script>
                document.getElementById('resetForm').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    const token = document.getElementById('token').value;
                    const password = document.getElementById('password').value;
                    const confirmPassword = document.getElementById('confirm_password').value;
                    
                    if (password !== confirmPassword) {{
                        document.getElementById('message').innerHTML = '<p class="error">❌ Passwords do not match</p>';
                        return;
                    }}
                    
                    const response = await fetch('/auth/reset-password', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token, new_password: password }})
                    }});
                    
                    const result = await response.json();
                    const messageDiv = document.getElementById('message');
                    
                    if (response.ok) {{
                        messageDiv.innerHTML = `<p class="success">✅ ${{result.message}}</p>`;
                        messageDiv.innerHTML += '<p>You can now <a href="/docs#/authentication/login">login</a> with your new password.</p>';
                    }} else {{
                        messageDiv.innerHTML = `<p class="error">❌ ${{result.detail || 'Error resetting password'}}</p>`;
                    }}
                }});
            </script>
        </body>
    </html>
    """



@router.post("/signup/caregiver", response_model=CaregiverSignupResponse)
async def signup_caregiver(
    caregiver_data: CaregiverSignupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new caregiver"""
    
    if not caregiver_data.agree_to_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must agree to the terms and conditions"
        )
    
    
    existing_user = db.query(User).filter(User.email == caregiver_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    
    base_username = f"{caregiver_data.first_name.lower()}.{caregiver_data.last_name.lower()}"
    username = base_username
    
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    
    hashed_password = get_pass_hash(caregiver_data.password)
    
    
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    caregiver_id = f"CG{''.join(random.choice(chars) for _ in range(8))}"
    
    
    while db.query(User).filter(User.caregiver_id == caregiver_id).first():
        caregiver_id = f"CG{''.join(random.choice(chars) for _ in range(8))}"
    
    
    user = User(
        email=caregiver_data.email,
        username=username,
        hashed_password=hashed_password,
        phone_number=caregiver_data.phone_number,
        is_caregiver=True,  
        is_email_verified=False
    )
    
    
    try:
        user.caregiver_id = caregiver_id
    except:
        pass  
    
    
    try:
        user.first_name = caregiver_data.first_name
    except:
        pass
    
    
    try:
        user.last_name = caregiver_data.last_name
    except:
        pass
    
    db.add(user)
    db.commit()
    db.refresh(user)  
    
    logger.info(f"✅ Caregiver user created: ID={user.id}, Email={user.email}")
    
    
    verification_token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    verification = EmailVerificationToken(
        user_id=user.id,  
        token=verification_token,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    
    background_tasks.add_task(
        email_service.send_caregiver_welcome_email,
        user.email,
        f"{caregiver_data.first_name} {caregiver_data.last_name}",
        caregiver_id,
        verification_token
    )
    
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_type="caregiver"
    )
    
    
    refresh_token = create_refresh_token(user.id, db)
    
    return {
        "caregiver_id": caregiver_id,
        "email": user.email,
        "first_name": caregiver_data.first_name,
        "last_name": caregiver_data.last_name,
        "caregiver_type": caregiver_data.caregiver_type,
        "message": f"Caregiver account created successfully. Your Caregiver ID is: {caregiver_id}",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "username": username
    }

@router.post("/signup", response_model=TokenResponse)
async def signup(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new patient user"""
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_data.username:
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    
    hashed_password = get_pass_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        phone_number=user_data.phone_number,
        is_email_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    
    verification_token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    verification = EmailVerificationToken(
        user_id=user.id,
        token=verification_token,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    
    background_tasks.add_task(
        email_service.send_welcome_email,
        user.email,
        user.username or user.email.split('@')[0],
        verification_token
    )
    
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_type="user"
    )
    
    refresh_token = create_refresh_token(user.id, db)
    
    
    session_token = generate_token()
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(session)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_type="user",
        user_id=user.id,
        email=user.email,
        is_email_verified=user.is_email_verified
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login with email and password"""
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_pass(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_type="user"
    )
    
    refresh_token = create_refresh_token(user.id, db)
    
    
    session_token = generate_token()
    device_info = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(session)
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_type="user",
        user_id=user.id,
        email=user.email,
        is_email_verified=user.is_email_verified
    )

@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if user:
        
        reset_token = generate_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        
        db.query(PasswordResetToken).filter(
            PasswordResetToken.email == request_data.email,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        
        
        reset_token_obj = PasswordResetToken(
            email=request_data.email,
            token=reset_token,
            expires_at=expires_at
        )
        
        db.add(reset_token_obj)
        db.commit()
        
        
        background_tasks.add_task(
            email_service.send_password_reset_email,
            request_data.email,
            reset_token
        )
    
    
    return {"message": "If your email exists, you will receive a password reset link"}

@router.post("/reset-password")
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == request_data.token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    
    user = db.query(User).filter(User.email == reset_token.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    
    user.hashed_password = get_pass_hash(request_data.new_password)
    reset_token.is_used = True
    
    
    db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"is_revoked": True})
    
    
    db.query(UserSession).filter(UserSession.user_id == user.id).update({"is_active": False})
    
    db.commit()
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    request_data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify email with token"""
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == request_data.token,
        EmailVerificationToken.expires_at > datetime.utcnow()
    ).first()
    
    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.query(User).filter(User.id == verification_token.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_email_verified = True
    db.delete(verification_token)
    db.commit()
    
    return {"message": "Email verified successfully"}

@router.post("/resend-verification")
async def resend_verification(
    request_data: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend email verification"""
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id
    ).delete()
    
    
    verification_token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    verification = EmailVerificationToken(
        user_id=user.id,
        token=verification_token,
        expires_at=expires_at
    )
    
    db.add(verification)
    db.commit()
    
    
    background_tasks.add_task(
        email_service.send_welcome_email,
        user.email,
        user.username or user.email.split('@')[0],
        verification_token
    )
    
    return {"message": "Verification email sent"}

@router.post("/login/otp/request")
async def request_otp_login(
    request_data: RequestOTPLogin,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request OTP for login - EMAIL ONLY VERSION"""
    user = db.query(User).filter(User.email == request_data.email).first()
    
    if not user:
        
        return {"message": "If your account exists, OTP will be sent to your email"}
    
    
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    
    db.query(LoginOTP).filter(
        LoginOTP.email == request_data.email,
        LoginOTP.is_used == False
    ).update({"is_used": True})
    
    
    login_otp = LoginOTP(
        email=request_data.email,
        otp=otp,
        expires_at=expires_at
    )
    
    db.add(login_otp)
    db.commit()
    
    
    background_tasks.add_task(
        email_service.send_otp_email,  
        user.email,
        user.username or user.email.split('@')[0],
        otp
    )
    
    return {
        "message": "OTP sent to your email address",
        "delivery_method": "email",
        "email": user.email[:3] + "***" + user.email.split('@')[1]  
    }

@router.post("/login/otp/verify")
async def verify_otp_login(
    request_data: VerifyOTPLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify OTP for login - EMAIL ONLY"""
    login_otp = db.query(LoginOTP).filter(
        LoginOTP.email == request_data.email,
        LoginOTP.otp == request_data.otp,
        LoginOTP.is_used == False,
        LoginOTP.expires_at > datetime.utcnow()
    ).first()
    
    if not login_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    
    login_otp.is_used = True
    
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_type="user"
    )
    
    refresh_token = create_refresh_token(user.id, db)
    
    
    session_token = generate_token()
    device_info = request.headers.get("User-Agent", "Unknown")
    ip_address = request.client.host if request.client else "Unknown"
    
    session = UserSession(
        user_id=user.id,
        session_token=session_token,
        device_info=device_info,
        ip_address=ip_address,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db.add(session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_type": "user",
        "user_id": user.id,
        "email": user.email,
        "is_email_verified": user.is_email_verified,
        "message": "Login successful via email OTP"
    }

@router.post("/change-password")
async def change_password(
    request_data: ChangePasswordRequest,
    current: Union[User, Admin] = Depends(get_current_user_or_admin),  
    db: Session = Depends(get_db)
):
    """Change password (works for both users and admins)"""
    from app.auth.hashing import verify_password as verify_pass
    
    
    if isinstance(current, Admin):
        if not verify_pass(request_data.current_password, current.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        current.hashed_password = get_pass_hash(request_data.new_password)
    else:
        if not verify_pass(request_data.current_password, current.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        current.hashed_password = get_pass_hash(request_data.new_password)
        
        
        db.query(RefreshToken).filter(RefreshToken.user_id == current.id).update({"is_revoked": True})
    
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.post("/token/refresh")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        user_type="user"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "user"
    }

@router.post("/logout")
async def logout(
    current: Union[User, Admin] = Depends(get_current_user_or_admin),  
    db: Session = Depends(get_db)
):
    """Logout user or admin"""
    if isinstance(current, Admin):
        
        return {"message": "Admin logged out successfully"}
    
    
    db.query(RefreshToken).filter(RefreshToken.user_id == current.id).update({"is_revoked": True})
    db.query(UserSession).filter(UserSession.user_id == current.id).update({"is_active": False})
    db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current: Union[User, Admin] = Depends(get_current_user_or_admin)  
):
    """Get current user or admin information"""
    if isinstance(current, Admin):
        
        return {
            "id": current.id,
            "email": current.email,
            "full_name": current.full_name,
            "is_superadmin": current.is_superadmin,
            "is_active": current.is_active,
            "user_type": "admin",
            "last_login": current.last_login,
            "created_at": current.created_at
        }
    else:
        
        return {
            "id": current.id,
            "email": current.email,
            "username": current.username,
            "patient_id": current.patient_id,
            "is_email_verified": current.is_email_verified,
            "is_active": current.is_active,
            "is_caregiver": current.is_caregiver,
            "phone_number": current.phone_number,
            "last_login": current.last_login,
            "created_at": current.created_at,
            "user_type": "user"
        }

@router.get("/sessions")
async def get_user_sessions(
    current: Union[User, Admin] = Depends(get_current_user_or_admin),  
    db: Session = Depends(get_db)
):
    """Get user's active sessions (also works for admin)"""
    
    
    if isinstance(current, Admin):
        
        
        return {
            "message": "Admin sessions are managed separately",
            "admin_id": current.id,
            "sessions": []
        }
    
    
    sessions = db.query(UserSession).filter(
        UserSession.user_id == current.id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).order_by(UserSession.last_activity.desc()).all()
    
    return [
        {
            "id": session.id,
            "device_info": session.device_info,
            "ip_address": session.ip_address,
            "last_activity": session.last_activity,
            "created_at": session.created_at
        }
        for session in sessions
    ]

from fastapi.responses import HTMLResponse, RedirectResponse


@router.get("/verify-email-page/{token}", response_class=HTMLResponse)
async def verify_email_page(
    token: str,
    db: Session = Depends(get_db)
):
    """HTML page to verify email (for direct links from emails)"""
    
    from app.models.auth import EmailVerificationToken
    from app.models.user import User
    
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.expires_at > datetime.utcnow()
    ).first()
    
    if not verification_token:
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Email Verification Failed</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .success { color: green; }
                    .error { color: red; }
                    .container { max-width: 600px; margin: 0 auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">Email Verification Failed</h1>
                    <p>The verification link is invalid or has expired.</p>
                    <p>Please request a new verification email.</p>
                    <p><a href="/docs#/authentication/resend_verification">Request New Verification Email</a></p>
                </div>
            </body>
        </html>
        """)
    
    user = db.query(User).filter(User.id == verification_token.user_id).first()
    if not user:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1>User not found</h1>
            </body>
        </html>
        """)
    
    
    user.is_email_verified = True
    db.delete(verification_token)
    db.commit()
    
    return HTMLResponse(content=f"""
    <html>
        <head>
            <title>Email Verified Successfully</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: green; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #4CAF50; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">Email Verified Successfully!</h1>
                <p>Your email has been verified. You can now log in to your account.</p>
                <p><strong>Email:</strong> {user.email}</p>
                <a href="/docs#/authentication/login" class="button">Go to Login</a>
                <p>Or use the API documentation to make login requests.</p>
            </div>
        </body>
    </html>
    """)

@router.get("/reset-password-page", response_class=HTMLResponse)
async def reset_password_page(
    token: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """HTML page to reset password (for direct links from emails)"""
    
    from app.models.auth import PasswordResetToken
    from app.models.user import User
    
    if not token:
        
        return HTMLResponse(content="""
        <html>
            <head>
                <title>Reset Password</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 50px; max-width: 500px; margin: 0 auto; }
                    .form-group { margin-bottom: 20px; }
                    label { display: block; margin-bottom: 5px; }
                    input { width: 100%; padding: 10px; box-sizing: border-box; }
                    button { padding: 12px 24px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
                    .error { color: red; }
                    .success { color: green; }
                </style>
            </head>
            <body>
                <h1>Reset Password</h1>
                <p>Please enter your reset token and new password.</p>
                <form id="resetForm">
                    <div class="form-group">
                        <label for="token">Reset Token (from email):</label>
                        <input type="text" id="token" name="token" required>
                    </div>
                    <div class="form-group">
                        <label for="password">New Password:</label>
                        <input type="password" id="password" name="password" minlength="8" required>
                    </div>
                    <button type="submit">Reset Password</button>
                </form>
                <div id="message"></div>
                <script>
                    document.getElementById('resetForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const token = document.getElementById('token').value;
                        const password = document.getElementById('password').value;
                        
                        const response = await fetch('/auth/reset-password', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ token, new_password: password })
                        });
                        
                        const result = await response.json();
                        const messageDiv = document.getElementById('message');
                        
                        if (response.ok) {
                            messageDiv.innerHTML = '<p class="success">' + result.message + '</p>';
                            messageDiv.innerHTML += '<p>You can now <a href="/docs#/authentication/login">login</a> with your new password.</p>';
                        } else {
                            messageDiv.innerHTML = '<p class="error">' + (result.detail || 'Error resetting password') + '</p>';
                        }
                    });
                </script>
            </body>
        </html>
        """)
    
    
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return HTMLResponse(content="""
        <html>
            <body>
                <h1 class="error">Invalid or Expired Token</h1>
                <p>The password reset token is invalid or has expired.</p>
                <p>Please request a new password reset.</p>
                <p><a href="/docs#/authentication/forgot_password">Request New Password Reset</a></p>
            </body>
        </html>
        """)
    
    
    return HTMLResponse(content=f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 50px; max-width: 500px; margin: 0 auto; }}
                .form-group {{ margin-bottom: 20px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input {{ width: 100%; padding: 10px; box-sizing: border-box; }}
                button {{ padding: 12px 24px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                .error {{ color: red; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>Set New Password</h1>
            <p>Please enter your new password.</p>
            <form id="resetForm">
                <input type="hidden" id="token" value="{token}">
                <div class="form-group">
                    <label for="password">New Password (min 8 characters):</label>
                    <input type="password" id="password" name="password" minlength="8" required>
                </div>
                <div class="form-group">
                    <label for="confirm_password">Confirm Password:</label>
                    <input type="password" id="confirm_password" name="confirm_password" minlength="8" required>
                </div>
                <button type="submit">Reset Password</button>
            </form>
            <div id="message"></div>
            <script>
                document.getElementById('resetForm').addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    const token = document.getElementById('token').value;
                    const password = document.getElementById('password').value;
                    const confirmPassword = document.getElementById('confirm_password').value;
                    
                    if (password !== confirmPassword) {{
                        document.getElementById('message').innerHTML = '<p class="error">Passwords do not match</p>';
                        return;
                    }}
                    
                    const response = await fetch('/auth/reset-password', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ token, new_password: password }})
                    }});
                    
                    const result = await response.json();
                    const messageDiv = document.getElementById('message');
                    
                    if (response.ok) {{
                        messageDiv.innerHTML = '<p class="success">' + result.message + '</p>';
                        messageDiv.innerHTML += '<p>You can now <a href="/docs#/authentication/login">login</a> with your new password.</p>';
                    }} else {{
                        messageDiv.innerHTML = '<p class="error">' + (result.detail || 'Error resetting password') + '</p>';
                    }}
                }});
            </script>
        </body>
    </html>
    """)

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    session = db.query(UserSession).filter(
        UserSession.id == session_id,
        UserSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.is_active = False
    db.commit()
    
    return {"message": "Session revoked"}