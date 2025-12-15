from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.auth.security import create_access_token, get_current_user
from app.auth.hashing import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=Token)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Validate that we have at least one identifier
        if not user_data.email and not user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either email or username must be provided"
            )
        
        # Check if user already exists
        if user_data.email:
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
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        # Generate patient ID
        db_user.patient_id = db_user.generate_patient_id()
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(db_user.id)}, 
            user_type="user"
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_type": "user"
        }
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        # Find user by username or email
        user = None
        if "@" in login_data.login:
            user = db.query(User).filter(User.email == login_data.login).first()
        else:
            user = db.query(User).filter(User.username == login_data.login).first()
        
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
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
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/google-auth", response_model=Token)
async def google_auth(google_token: str, db: Session = Depends(get_db)):
    try:
        # Mock Google OAuth implementation
        user = db.query(User).filter(User.google_id == google_token).first()
        if not user:
            user = User(
                google_id=google_token, 
                email=f"google_{google_token[:10]}@example.com",
                username=f"google_user_{google_token[:8]}"
            )
            user.patient_id = user.generate_patient_id()
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            user_type="user"
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_type": "user"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google auth error: {str(e)}"
        )

@router.post("/apple-auth", response_model=Token)
async def apple_auth(apple_token: str, db: Session = Depends(get_db)):
    try:
        # Mock Apple Sign-in implementation
        user = db.query(User).filter(User.apple_id == apple_token).first()
        if not user:
            user = User(
                apple_id=apple_token, 
                email=f"apple_{apple_token[:10]}@example.com",
                username=f"apple_user_{apple_token[:8]}"
            )
            user.patient_id = user.generate_patient_id()
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            user_type="user"
        )
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user_type": "user"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Apple auth error: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user