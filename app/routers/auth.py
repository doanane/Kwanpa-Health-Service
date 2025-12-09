from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.database import get_db
from app.auth.security import create_access_token, get_current_user
from app.auth.hashing import verify_password, get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, SignupResponse, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        if not user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        
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
        
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return SignupResponse(
            message="User registered successfully. Please login.",
            user_id=db_user.id,
            patient_id=db_user.patient_id,
            email=db_user.email
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database constraint violated"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
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
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.hashed_password or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        if not user.patient_id:
            user.patient_id = user.generate_patient_id()
            db.commit()
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            user_type="user"
        )
        return Token(
            access_token=access_token, 
            token_type="bearer",
            user_type="user"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@router.post("/google-auth", response_model=Token)
async def google_auth(google_token: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.google_id == google_token).first()
        if not user:
            user = User(
                google_id=google_token, 
                email=f"google_{google_token[:10]}@example.com",
                username=f"google_user_{google_token[:8]}"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            user_type="user"
        )
        return Token(
            access_token=access_token, 
            token_type="bearer",
            user_type="user"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google auth error: {str(e)}"
        )

@router.post("/apple-auth", response_model=Token)
async def apple_auth(apple_token: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.apple_id == apple_token).first()
        if not user:
            user = User(
                apple_id=apple_token, 
                email=f"apple_{apple_token[:10]}@example.com",
                username=f"apple_user_{apple_token[:8]}"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        access_token = create_access_token(
            data={"sub": str(user.id)}, 
            user_type="user"
        )
        return Token(
            access_token=access_token, 
            token_type="bearer",
            user_type="user"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Apple auth error: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user