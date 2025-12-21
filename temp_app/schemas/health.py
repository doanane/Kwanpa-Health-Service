from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class HealthDataBase(BaseModel):
    steps: Optional[int] = Field(0, description="Number of steps taken")
    sleep_time: Optional[int] = Field(None, description="Sleep duration in minutes")
    wake_up_time: Optional[datetime] = Field(None, description="Wake up time")
    water_intake: Optional[int] = Field(None, description="Water intake in ml")
    blood_pressure: Optional[str] = Field(None, description="Blood pressure reading")
    heart_rate: Optional[int] = Field(None, description="Heart rate in BPM")
    blood_glucose: Optional[float] = Field(None, description="Blood glucose level")
    calories_burned: Optional[int] = Field(0, description="Calories burned")

class HealthDataCreate(HealthDataBase):
    pass

class HealthDataResponse(HealthDataBase):
    id: int
    user_id: int
    date: datetime
    
    model_config = ConfigDict(from_attributes=True)

class FoodLogBase(BaseModel):
    meal_type: str = Field(..., description="Type of meal (breakfast, lunch, dinner, snack)")
    diet_score: Optional[int] = Field(None, description="Diet score from 0-100")

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
    progress_score: int = Field(..., description="Progress score from 0-100")
    progress_color: str = Field(..., description="Progress color (red, orange, yellow, green)")

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
    recent_meals: List[Dict[str, Any]] = []  # Add this
    meal_count_today: int = 0  # Add this
    
    model_config = ConfigDict(from_attributes=True)
    
class ProgressUpdateRequest(BaseModel):
    progress_score: int = Field(..., ge=0, le=100, description="Progress score from 0 to 100")