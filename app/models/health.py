
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  
from app.database import Base

class HealthData(Base):
    __tablename__ = "health_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True), server_default=func.now())
    steps = Column(Integer, default=0)
    sleep_time = Column(Integer)
    wake_up_time = Column(DateTime, nullable=True)
    water_intake = Column(Integer)
    blood_pressure = Column(String)
    heart_rate = Column(Integer)
    blood_glucose = Column(Float)
    calories_burned = Column(Integer, default=0)
    
    
    user = relationship("User", back_populates="health_data")

class FoodLog(Base):
    __tablename__ = "food_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_type = Column(String)
    food_image_url = Column(String, nullable=True)
    ai_analysis = Column(JSONB)
    diet_score = Column(Integer)
    nutrients = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="food_logs")

class WeeklyProgress(Base):
    __tablename__ = "weekly_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_start_date = Column(DateTime)
    week_end_date = Column(DateTime)
    progress_score = Column(Integer)
    progress_color = Column(String)
    steps_goal = Column(Integer, default=10000)
    sleep_goal = Column(Integer, default=480)
    water_goal = Column(Integer, default=2000)
    
    user = relationship("User", back_populates="weekly_progress")

class HealthInsight(Base):
    __tablename__ = "health_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    insight_type = Column(String)
    message = Column(Text)
    severity = Column(String)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_resolved = Column(Boolean, default=False)