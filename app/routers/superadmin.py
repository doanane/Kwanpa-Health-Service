from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth.security import create_access_token
from app.auth.hashing import verify_password
from app.models.admin import Admin
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/superadmin", tags=["superadmin"])


class AdminLoginRequest(BaseModel):
    email: EmailStr = Field(..., example="superadmin@hewal3.com")
    password: str = Field(..., example="Admin@123")

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    admin: dict

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Admin login with email and password"""
    print(f"DEBUG: Login attempt for email: {request.email}")
    
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    
    if not admin:
        print(f"DEBUG: Admin not found for email: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    print(f"DEBUG: Found admin - ID: {admin.id}, Email: {admin.email}")
    print(f"DEBUG: Hashed password exists: {bool(admin.hashed_password)}")
    
    
    if admin.hashed_password:
        print(f"DEBUG: Hash (first 30 chars): {admin.hashed_password[:30]}...")
    
    
    print(f"DEBUG: Testing password: {request.password}")
    from app.auth.hashing import get_password_hash
    test_hash = get_password_hash(request.password)
    print(f"DEBUG: Test hash (first 30 chars): {test_hash[:30]}...")
    print(f"DEBUG: Hashes match: {admin.hashed_password == test_hash}")
    
    if not verify_password(request.password, admin.hashed_password):
        print(f"DEBUG: Password verification FAILED")
        print(f"DEBUG: Stored hash: {admin.hashed_password[:50]}...")
        print(f"DEBUG: Computed hash: {test_hash[:50]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    print(f"DEBUG: Password verification SUCCESS")
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is deactivated"
        )
    
    
    admin.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": admin.email},
        user_type="admin"
    )
    
    return AdminLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_type="admin",
        admin={
            "id": admin.id,
            "email": admin.email,
            "full_name": admin.full_name,
            "is_superadmin": admin.is_superadmin,
            "is_active": admin.is_active,
            "last_login": admin.last_login.isoformat() if admin.last_login else None
        }
    )
    
@router.get("/test")
async def test_superadmin():
    """Test endpoint to verify superadmin router is working"""
    return {"message": "Superadmin router is working!"}


@router.get("/debug")
async def debug_admin_data(db: Session = Depends(get_db)):
    """Debug endpoint to see what's in the admin table"""
    try:
        admins = db.query(Admin).all()
        result = []
        for admin in admins:
            result.append({
                "id": admin.id,
                "email": admin.email,
                "hashed_password": "Yes" if admin.hashed_password else "No",
                "full_name": admin.full_name,
                "is_superadmin": admin.is_superadmin,
                "is_active": admin.is_active,
                "created_at": admin.created_at.isoformat() if admin.created_at else None
            })
        return {"admins": result, "count": len(result)}
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}