from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime

class HealthDataBase(BaseModel):
    steps: Optional[int] = 0
    sleep_time: Optional[int] = None
    wake_up_time: Optional[datetime] = None
    water_intake: Optional[int] = None
    blood_pressure: Optional[str] = None
    heart_rate: Optional[int] = None
    blood_glucose: Optional[float] = None
    calories_burned: Optional[int] = 0

class HealthDataCreate(HealthDataBase):
    pass

class HealthDataResponse(HealthDataBase):
    id: int
    user_id: int
    date: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FoodLogBase(BaseModel):
    meal_type: str
    diet_score: Optional[int] = None

class FoodLogCreate(FoodLogBase):
    pass

class FoodLogResponse(FoodLogBase):
    id: int
    user_id: int
    food_image_url: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    nutrients: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class WeeklyProgressBase(BaseModel):
    progress_score: int
    progress_color: str

class WeeklyProgressResponse(WeeklyProgressBase):
    id: int
    user_id: int
    week_start_date: datetime
    week_end_date: datetime
    steps_goal: int
    sleep_goal: int
    water_goal: int
    
    model_config = ConfigDict(from_attributes=True)

class HealthInsightResponse(BaseModel):
    id: int
    user_id: int
    insight_type: str
    message: str
    severity: str
    generated_at: datetime
    is_resolved: bool
    
    model_config = ConfigDict(from_attributes=True)

class HealthDashboardResponse(BaseModel):
    welcome_message: str
    weekly_progress: WeeklyProgressResponse
    health_snapshot: HealthDataResponse
    diet_score: Optional[int] = None
    daily_tip: Optional[str] = None