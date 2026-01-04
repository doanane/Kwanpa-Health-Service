from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.database import get_db
from app.auth.security import get_current_active_user  
from app.models.user import User, UserProfile
from app.models.health import HealthData, FoodLog, WeeklyProgress, HealthInsight
from app.schemas.health import (
    HealthDataCreate, HealthDataResponse, 
    FoodLogCreate, FoodLogResponse, 
    WeeklyProgressResponse, HealthDashboardResponse, 
    ProgressUpdateRequest,
    ActivityRing, HealthTrend, HealthCategory, DailyHealthScore
)

router = APIRouter(prefix="/health", tags=["health"])

def get_daily_tip():
    tips = [
        "Walking 30 minutes a day can lower blood pressure.",
        "Hydration is key! Drink water before every meal.",
        "Better sleep starts with a consistent bedtime routine.",
        "Reduce sugar intake to improve energy levels.",
        "Stretching daily improves flexibility and reduces pain.",
        "Mindfulness meditation can lower stress in 10 minutes.",
        "Eating slowly helps with digestion and weight control."
    ]
    return random.choice(tips)

@router.get("/dashboard", response_model=HealthDashboardResponse)
async def get_health_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
    
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    welcome_name = profile.full_name if profile else current_user.username
    
    
    
    
    health_data = db.query(HealthData).filter(
        HealthData.user_id == current_user.id
    ).order_by(HealthData.date.desc()).first()
    
    
    if not health_data:
        health_data = HealthData(
            user_id=current_user.id,
            steps=0,
            sleep_time=480,
            water_intake=0,
            blood_pressure="120/80",
            heart_rate=72,
            blood_glucose=90.0,
            calories_burned=0,
            date=datetime.now()
        )
        db.add(health_data)
        db.commit()
        db.refresh(health_data)

    
    steps = health_data.steps if health_data.steps is not None else 0
    calories = health_data.calories_burned if health_data.calories_burned is not None else 0
    water = health_data.water_intake if health_data.water_intake is not None else 0
    
    
    
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if not weekly_progress:
        weekly_progress = WeeklyProgress(
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_end,
            progress_score=0,
            progress_color="red",
            steps_goal=10000,
            sleep_goal=480,
            water_goal=2000
        )
        db.add(weekly_progress)
        db.commit()
        db.refresh(weekly_progress)
    
    
    
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.created_at >= today_start
    ).order_by(FoodLog.created_at.desc()).limit(5).all()
    
    recent_meals = []
    for log in today_food_logs:
        recent_meals.append({
            "id": log.id,
            "meal_type": log.meal_type,
            "detected_food": log.ai_analysis.get('detected_food', 'Unknown') if log.ai_analysis else 'Unknown',
            "diet_score": log.diet_score,
            "created_at": log.created_at
        })
    
    diet_score = 0
    if today_food_logs:
        total_diet = sum(log.diet_score or 0 for log in today_food_logs)
        diet_score = total_diet // len(today_food_logs)
    
    
    
    
    
    
    rings = ActivityRing(
        move=calories,
        move_goal=600,
        exercise=25, 
        exercise_goal=30,
        stand=8,     
        stand_goal=12
    )

    
    score_val = 60 
    if steps > 5000: score_val += 15
    if steps > 8000: score_val += 10
    if water > 1500: score_val += 5
    if diet_score > 70: score_val += 10
    
    if score_val > 100: score_val = 100
    
    daily_score_obj = DailyHealthScore(
        score=score_val,
        message=f"Welcome, {welcome_name}. You're active today!",
        trend_percentage=12
    )

    
    trends = [
        HealthTrend(category="Walking", icon="walk", value=f"{steps} steps", trend="up", message="Above average walking pace."),
        HealthTrend(category="Active Energy", icon="flame", value=f"{calories} kcal", trend="up", message="Burning calories well."),
        HealthTrend(category="Sleep", icon="bed", value="6h 45m", trend="down", message="Try to sleep earlier."),
        HealthTrend(category="Stand", icon="body", value="8 hr", trend="neutral", message="Meeting stand goals."),
    ]

    
    categories = [
        
        HealthCategory(id="rings", title="Activity", value=f"{int((calories/600)*100)}%", unit="goal", icon="aperture", color="#E11D48", is_workout=False),
        HealthCategory(id="steps", title="Steps", value=f"{steps:,}", unit="steps", icon="footsteps", color="#F59E0B", is_workout=False),
        
        
        HealthCategory(id="hr", title="Heart Rate", value=f"{health_data.heart_rate or 72}", unit="BPM", icon="heart", color="#FF3B30", is_workout=False),
        HealthCategory(id="bp", title="Blood Pressure", value=f"{health_data.blood_pressure or '120/80'}", unit="mmHg", icon="pulse", color="#FF3B30", is_workout=False),
        HealthCategory(id="oxy", title="Blood Oxygen", value="98", unit="%", icon="water", color="#5AC8FA", is_workout=False),
        
        
        HealthCategory(id="water", title="Water Intake", value=f"{water}", unit="ml", icon="water", color="#007AFF", is_workout=False),
        HealthCategory(id="sleep", title="Sleep Analysis", value="6h 45m", unit="in bed", icon="bed", color="#FF9500", is_workout=False),
        HealthCategory(id="mind", title="Mindfulness", value="12", unit="min", icon="leaf", color="#34C759", is_workout=False),

        
        HealthCategory(id="run", title="Outdoor Run", value="5.0", unit="km", icon="walk", color="#34C759", is_workout=True),
        HealthCategory(id="cycle", title="Cycling", value="12.4", unit="km", icon="bicycle", color="#34C759", is_workout=True),
        HealthCategory(id="swim", title="Swimming", value="--", unit="m", icon="water", color="#34C759", is_workout=True),
    ]

    return HealthDashboardResponse(
        
        welcome_message=f"Welcome, {welcome_name}",
        weekly_progress=weekly_progress,
        health_snapshot=health_data,
        diet_score=diet_score,
        daily_tip=get_daily_tip(),
        recent_meals=recent_meals,
        meal_count_today=len(today_food_logs),
        
        
        daily_score=daily_score_obj,
        activity_rings=rings,
        trends=trends,
        categories=categories
    )

@router.post("/food-log", response_model=FoodLogResponse)
async def log_food(
    food_data: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    
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
        ai_analysis=ai_analysis,
        nutrients=ai_analysis["nutrients"]
    )
    
    db.add(food_log)
    db.commit()
    db.refresh(food_log)
    return food_log

@router.get("/weekly-progress", response_model=WeeklyProgressResponse)
async def get_weekly_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= week_start
    ).first()
    
    if not progress:
        
        return WeeklyProgressResponse(
            id=0,
            user_id=current_user.id,
            week_start_date=week_start,
            week_end_date=week_start + timedelta(days=6),
            progress_score=0,
            progress_color="gray",
            steps_goal=10000,
            sleep_goal=480,
            water_goal=2000
        )
    
    return progress

@router.get("/health-snapshot", response_model=HealthDataResponse)
async def get_health_snapshot(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    snapshot = db.query(HealthData).filter(
        HealthData.user_id == current_user.id
    ).order_by(HealthData.date.desc()).first()
    
    if not snapshot:
        snapshot = HealthData(
            user_id=current_user.id,
            steps=0,
            sleep_time=480,
            water_intake=2000,
            blood_pressure="120/80",
            heart_rate=72,
            blood_glucose=90.0,
            date=datetime.now()
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
    
    return snapshot
    

@router.post("/health-data", response_model=HealthDataResponse)
async def add_health_data(
    health_data: HealthDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data_dict = health_data.dict()
    data_dict['date'] = datetime.now()
    health_record = HealthData(user_id=current_user.id, **data_dict)
    db.add(health_record)
    db.commit()
    db.refresh(health_record)
    return health_record

@router.get("/food-logs", response_model=list[FoodLogResponse])
async def get_food_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    logs = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id
    ).order_by(FoodLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/update-progress")
async def update_weekly_progress(
    progress_data: ProgressUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
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