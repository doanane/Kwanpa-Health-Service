from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.database import get_db
from app.auth.security import get_current_user
from app.models.user import User, UserProfile
from app.models.health import HealthData, FoodLog, WeeklyProgress
from app.schemas.health import HealthDataCreate, HealthDataResponse, FoodLogCreate, FoodLogResponse, WeeklyProgressResponse, HealthDashboardResponse

router = APIRouter(prefix="/health", tags=["health"])

def get_daily_tip():
    tips = [
        "Try reducing salt intake this week",
        "Increase your water consumption to 8 glasses daily",
        "Consider adding a 30-minute walk to your routine",
        "Include more leafy greens in your meals",
        "Monitor your sugar intake carefully",
        "Practice mindful eating habits",
        "Get at least 7-8 hours of sleep nightly"
    ]
    return random.choice(tips)

@router.get("/dashboard", response_model=HealthDashboardResponse)
async def get_health_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get user profile for welcome message
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    welcome_name = profile.full_name if profile else "User"
    
    # Get latest health data
    health_data = db.query(HealthData).filter(
        HealthData.user_id == current_user.id
    ).order_by(HealthData.date.desc()).first()
    
    # Get current week's progress
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if not weekly_progress:
        # Create default weekly progress
        weekly_progress = WeeklyProgress(
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            progress_score=0,
            progress_color="red"
        )
        db.add(weekly_progress)
        db.commit()
        db.refresh(weekly_progress)
    
    # Get today's food logs for diet score
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.created_at >= today_start
    ).all()
    
    diet_score = None
    if today_food_logs:
        diet_score = sum(log.diet_score or 0 for log in today_food_logs) // len(today_food_logs)
    
    daily_tip = get_daily_tip()
    
    return HealthDashboardResponse(
        welcome_message=f"Welcome, {welcome_name}. I hope you are doing well today. Check in for your weekly progress.",
        weekly_progress=weekly_progress,
        health_snapshot=health_data or HealthDataResponse(
            id=0, user_id=current_user.id, date=datetime.now()
        ),
        diet_score=diet_score,
        daily_tip=daily_tip
    )

@router.post("/food-log", response_model=FoodLogResponse)
async def log_food(
    food_data: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Mock AI analysis
    ai_analysis = {
        "analysis": "Food analyzed successfully",
        "nutrients": {
            "protein": random.randint(10, 30),
            "carbs": random.randint(20, 60),
            "fats": random.randint(5, 20)
        },
        "recommendations": ["Good balance of nutrients", "Consider adding more vegetables"]
    }
    
    food_log = FoodLog(
        user_id=current_user.id,
        meal_type=food_data.meal_type,
        diet_score=food_data.diet_score or random.randint(60, 95),
        ai_analysis=str(ai_analysis)
    )
    
    db.add(food_log)
    db.commit()
    db.refresh(food_log)
    return food_log

@router.get("/weekly-progress", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weekly progress not found"
        )
    
    return progress

@router.get("/health-snapshot", response_model=HealthDataResponse)
async def get_health_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    snapshot = db.query(HealthData).filter(
        HealthData.user_id == current_user.id
    ).order_by(HealthData.date.desc()).first()
    
    if not snapshot:
        # Create default health data
        snapshot = HealthData(
            user_id=current_user.id,
            steps=0,
            sleep_time=480,
            water_intake=2000,
            blood_pressure="120/80",
            heart_rate=72,
            blood_glucose=90.0
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
    
    return snapshot

@router.post("/health-data", response_model=HealthDataResponse)
async def add_health_data(
    health_data: HealthDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    health_record = HealthData(user_id=current_user.id, **health_data.dict())
    db.add(health_record)
    db.commit()
    db.refresh(health_record)
    return health_record

@router.get("/food-logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id
    ).order_by(FoodLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/update-progress")
async def update_weekly_progress(
    progress_score: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Determine progress color
    if progress_score >= 80:
        progress_color = "green"
    elif progress_score >= 60:
        progress_color = "yellow"
    elif progress_score >= 40:
        progress_color = "orange"
    else:
        progress_color = "red"
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if weekly_progress:
        weekly_progress.progress_score = progress_score
        weekly_progress.progress_color = progress_color
    else:
        weekly_progress = WeeklyProgress(
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            progress_score=progress_score,
            progress_color=progress_color
        )
        db.add(weekly_progress)
    
    db.commit()
    return {"message": "Progress updated successfully"}