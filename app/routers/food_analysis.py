from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import os
import uuid
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User, UserProfile
from app.models.health import FoodLog
from app.services.azure_ai import azure_ai_service
from app.services.azure_storage import azure_storage_service
from app.services.email_service import email_service
from app.config import settings
from pydantic import BaseModel, Field
import json

router = APIRouter(prefix="/food", tags=["food_analysis"])

# Pydantic Models
class FoodAnalysisResponse(BaseModel):
    food_id: int
    meal_type: str
    detected_food: str
    description: str
    nutrients: dict
    diet_score: int
    recommendation: str
    image_url: Optional[str]
    created_at: datetime

class MealAnalysisRequest(BaseModel):
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack")
    notes: Optional[str] = None

# Helper Functions
def calculate_diet_score(nutrients: dict, user_conditions: list) -> int:
    """Calculate diet score based on nutrients and user conditions"""
    score = 70  # Base score
    
    # Adjust based on nutrients
    calories = nutrients.get("calories", 500)
    if 300 <= calories <= 500:
        score += 10
    elif calories > 700:
        score -= 15
    
    carbs = nutrients.get("carbs", 50)
    if carbs < 40:
        score += 5
    elif carbs > 70:
        score -= 10
    
    protein = nutrients.get("protein", 15)
    if protein > 20:
        score += 10
    elif protein < 10:
        score -= 5
    
    # Adjust for diabetes
    if "diabetes" in user_conditions:
        if carbs > 60:
            score -= 20
        if nutrients.get("type") == "starch":
            score -= 15
    
    # Adjust for hypertension
    if "hypertension" in user_conditions:
        # In real app, check sodium content
        if nutrients.get("type") == "processed":
            score -= 15
    
    # Adjust for obesity
    if "obesity" in user_conditions:
        if calories > 600:
            score -= 20
    
    # Ensure score is between 0-100
    return max(0, min(100, score))

def save_food_image(file: UploadFile) -> str:
    """Save food image to local storage (in production, use Azure Blob)"""
    os.makedirs("uploads/food", exist_ok=True)
    
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join("uploads/food", filename)
    
    with open(filepath, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return filepath

# Endpoints
@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(
    meal_type: str,
    file: UploadFile = File(...),
    notes: