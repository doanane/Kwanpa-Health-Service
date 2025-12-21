from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class FoodAnalysis(Base):
    __tablename__ = "food_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_url = Column(String)  
    detected_foods = Column(JSON)  
    ghanaian_foods = Column(JSON)  
    nutritional_info = Column(JSON)  
    health_score = Column(Integer)  
    recommendations = Column(JSON)  
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="food_analyses")