from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User
from app.models.health import WeeklyProgress

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/weekly")
async def get_weekly_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get current week's progress for all users
    current_week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.week_start_date >= current_week_start,
        WeeklyProgress.progress_score > 0
    ).order_by(desc(WeeklyProgress.progress_score)).limit(50).all()
    
    leaderboard = []
    for progress in weekly_progress:
        user = db.query(User).filter(User.id == progress.user_id).first()
        if user and user.is_active:
            leaderboard.append({
                "rank": len(leaderboard) + 1,
                "patient_id": user.patient_id,
                "progress_score": progress.progress_score,
                "progress_color": progress.progress_color,
                "steps": progress.steps_goal,
                "sleep_achieved": progress.sleep_goal,
                "water_achieved": progress.water_goal
            })
    
    return {
        "week_start": current_week_start,
        "leaderboard": leaderboard,
        "current_user_rank": next(
            (item["rank"] for item in leaderboard if item["patient_id"] == current_user.patient_id), 
            None
        )
    }

@router.get("/history")
async def get_user_progress_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Get user's historical progress
    historical_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id
    ).order_by(desc(WeeklyProgress.week_start_date)).limit(52).all()  # Last year
    
    history = []
    for progress in historical_progress:
        history.append({
            "week_start": progress.week_start_date,
            "week_end": progress.week_end_date,
            "progress_score": progress.progress_score,
            "progress_color": progress.progress_color,
            "steps_achieved": progress.steps_goal,
            "sleep_achieved": progress.sleep_goal,
            "water_achieved": progress.water_goal
        })
    
    return {
        "patient_id": current_user.patient_id,
        "progress_history": history
    }

@router.get("/achievements")
async def get_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Calculate user achievements
    total_weeks = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id
    ).count()
    
    green_weeks = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.progress_color == "green"
    ).count()
    
    consecutive_green_weeks = 0
    current_streak = 0
    
    # Get weekly progress in chronological order
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id
    ).order_by(WeeklyProgress.week_start_date).all()
    
    for progress in weekly_progress:
        if progress.progress_color == "green":
            current_streak += 1
            consecutive_green_weeks = max(consecutive_green_weeks, current_streak)
        else:
            current_streak = 0
    
    achievements = []
    if total_weeks >= 4:
        achievements.append("4-Week Veteran")
    if green_weeks >= 10:
        achievements.append("Health Champion")
    if consecutive_green_weeks >= 4:
        achievements.append("Monthly Master")
    if total_weeks >= 52:
        achievements.append("Year of Health")
    
    return {
        "patient_id": current_user.patient_id,
        "total_weeks_tracked": total_weeks,
        "green_weeks": green_weeks,
        "longest_green_streak": consecutive_green_weeks,
        "achievements": achievements
    }