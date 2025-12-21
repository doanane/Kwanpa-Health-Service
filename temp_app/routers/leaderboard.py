from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User
from app.models.health import WeeklyProgress, HealthData

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/weekly")
async def get_weekly_leaderboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    weekly_progress = db.query(
        WeeklyProgress,
        User
    ).join(
        User, User.id == WeeklyProgress.user_id
    ).filter(
        WeeklyProgress.week_start_date >= week_start
    ).order_by(
        desc(WeeklyProgress.progress_score)
    ).limit(20).all()
    
    leaderboard = []
    for rank, (progress, user) in enumerate(weekly_progress, 1):
        leaderboard.append({
            "rank": rank,
            "user_id": user.patient_id,
            "display_name": f"User{user.patient_id[-4:]}" if user.patient_id else f"User{user.id}",
            "progress_score": progress.progress_score,
            "progress_color": progress.progress_color,
            "steps_completed": progress.steps_goal,
            "is_current_user": user.id == current_user.id
        })
    
    current_user_rank = None
    current_user_data = None
    for item in leaderboard:
        if item["is_current_user"]:
            current_user_rank = item["rank"]
            current_user_data = item
            break
    
    if not current_user_data:
        user_progress = db.query(WeeklyProgress).filter(
            WeeklyProgress.user_id == current_user.id,
            WeeklyProgress.week_start_date >= week_start
        ).first()
        
        if user_progress:
            current_user_rank = len(leaderboard) + 1
            current_user_data = {
                "rank": current_user_rank,
                "user_id": current_user.patient_id,
                "display_name": f"User{current_user.patient_id[-4:]}" if current_user.patient_id else f"User{current_user.id}",
                "progress_score": user_progress.progress_score,
                "progress_color": user_progress.progress_color,
                "steps_completed": user_progress.steps_goal,
                "is_current_user": True
            }
    
    return {
        "week_start": week_start.date().isoformat(),
        "total_participants": len(leaderboard),
        "leaderboard": leaderboard[:10],
        "current_user_rank": current_user_rank,
        "current_user_data": current_user_data
    }

@router.get("/history")
async def get_user_progress_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    progress_history = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id,
        WeeklyProgress.week_start_date >= start_date
    ).order_by(
        WeeklyProgress.week_start_date
    ).all()
    
    health_history = db.query(HealthData).filter(
        HealthData.user_id == current_user.id,
        HealthData.date >= start_date
    ).order_by(
        HealthData.date
    ).all()
    
    history_data = []
    for progress in progress_history:
        week_health = [h for h in health_history if h.date >= progress.week_start_date and h.date <= progress.week_end_date]
        
        avg_heart_rate = None
        avg_steps = None
        
        if week_health:
            heart_rates = [h.heart_rate for h in week_health if h.heart_rate]
            if heart_rates:
                avg_heart_rate = sum(heart_rates) / len(heart_rates)
            
            steps = [h.steps for h in week_health if h.steps]
            if steps:
                avg_steps = sum(steps) / len(steps)
        
        history_data.append({
            "week_start": progress.week_start_date.date().isoformat(),
            "week_end": progress.week_end_date.date().isoformat(),
            "progress_score": progress.progress_score,
            "progress_color": progress.progress_color,
            "avg_heart_rate": avg_heart_rate,
            "avg_steps": avg_steps,
            "achievements": ["Weekly Goal Met"] if progress.progress_score >= 80 else []
        })
    
    return {
        "user_id": current_user.patient_id,
        "period_days": days,
        "total_weeks": len(history_data),
        "history": history_data
    }

@router.get("/achievements")
async def get_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    achievements = []
    
    weekly_progress = db.query(WeeklyProgress).filter(
        WeeklyProgress.user_id == current_user.id
    ).order_by(
        desc(WeeklyProgress.week_start_date)
    ).limit(4).all()
    
    consecutive_weeks = 0
    for i in range(len(weekly_progress) - 1):
        if weekly_progress[i].progress_score >= 80 and weekly_progress[i+1].progress_score >= 80:
            consecutive_weeks += 1
        else:
            break
    
    if consecutive_weeks >= 4:
        achievements.append({
            "id": "consecutive_4_weeks",
            "name": "Consistency Champion",
            "description": "Maintained excellent progress for 4 consecutive weeks",
            "icon": "🏆",
            "unlocked_at": datetime.now().isoformat()
        })
    
    health_data = db.query(HealthData).filter(
        HealthData.user_id == current_user.id
    ).order_by(
        desc(HealthData.date)
    ).limit(30).all()
    
    if health_data:
        avg_heart_rate = sum([h.heart_rate for h in health_data if h.heart_rate]) / len([h for h in health_data if h.heart_rate])
        if avg_heart_rate and avg_heart_rate < 80:
            achievements.append({
                "id": "healthy_heart",
                "name": "Heart Health Guardian",
                "description": "Maintained healthy heart rate for 30 days",
                "icon": "❤️",
                "unlocked_at": datetime.now().isoformat()
            })
    
    total_steps = sum([h.steps for h in health_data if h.steps])
    if total_steps and total_steps > 100000:
        achievements.append({
            "id": "step_master",
            "name": "Step Master",
            "description": "Walked over 100,000 steps",
            "icon": "👣",
            "unlocked_at": datetime.now().isoformat()
        })
    
    profile_completion = db.query(User).filter(User.id == current_user.id).first()
    if profile_completion and profile_completion.profile and profile_completion.profile[0].profile_completed:
        achievements.append({
            "id": "profile_complete",
            "name": "Getting Started",
            "description": "Completed your health profile",
            "icon": "✅",
            "unlocked_at": profile_completion.profile[0].created_at.isoformat() if hasattr(profile_completion.profile[0], 'created_at') else datetime.now().isoformat()
        })
    
    return {
        "user_id": current_user.patient_id,
        "total_achievements": len(achievements),
        "achievements": achievements
    }