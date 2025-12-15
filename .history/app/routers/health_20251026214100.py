from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User, UserProfile
from app.models.health import HealthData, FoodLog, WeeklyProgress, HealthInsight
from app.schemas.health import HealthDataCreate, HealthDataResponse, FoodLogCreate, FoodLogResponse, WeeklyProgressResponse, HealthDashboardResponse, ProgressUpdateRequest

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
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.post("/food-log", response_model=FoodLogResponse)
async def log_food(
    food_data: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/weekly-progress", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/health-snapshot", response_model=HealthDataResponse)
async def get_health_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.post("/health-data", response_model=HealthDataResponse)
async def add_health_data(
    health_data: HealthDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.get("/food-logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Implementation remains the same...
    # [Previous implementation code...]

@router.post("/update-progress")
async def update_weekly_progress(
    progress_data: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    # Determine progress color
    if progress_data.progress_score >= 80:
        progress_color = "green"
    elif progress_data.progress_score >= 60:
        progress_color = "yellow"
    elif progress_data.progress_score >= 40:
        progress_color = "orange"
    else:
        progress_color = "red"
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if weekly_progress:
        weekly_progress.progress_score = progress_data.progress_score
        weekly_progress.progress_color = progress_color
    else:
        weekly_progress = WeeklyProgress(
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            progress_score=progress_data.progress_score,
            progress_color=progress_color,
            steps_goal=10000,
            sleep_goal=480,
            water_goal=2000
        )
        db.add(weekly_progress)
    
    db.commit()
    return {"message": "Progress updated successfully"}