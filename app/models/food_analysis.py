from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class FoodAnalysis(Base):
    __tablename__ = "food_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String)  # Azure Blob Storage URL
    detected_foods = Column(JSON)  # List of detected foods
    ghanaian_foods = Column(JSON)  # Ghanaian-specific food detection
    nutritional_info = Column(JSON)  # Calories, carbs, protein, fats
    health_score = Column(Integer)  # 0-100 score
    recommendations = Column(JSON)  # AI recommendations
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="food_analyses")