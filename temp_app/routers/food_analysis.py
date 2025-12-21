from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import os
from datetime import datetime
import tempfile

from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User
from app.models.health import FoodLog
from app.services.azure_ai import azure_ai_service
from app.schemas.health import FoodLogResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["food_analysis"])

@router.post("/analyze-meal", response_model=dict)
async def analyze_meal(
    meal_type: str = Form(..., description="Type of meal: breakfast, lunch, dinner, snack"),
    file: UploadFile = File(..., description="Image of the meal"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a meal image using Azure AI Vision.
    
    This endpoint:
    1. Accepts an image upload
    2. Sends it to Azure AI Vision for analysis
    3. Returns food tags and nutritional estimates
    4. Saves the analysis to the database
    """
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 10MB"
        )
    
    # Create temp file for processing
    temp_dir = tempfile.gettempdir()
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    temp_filename = f"meal_{uuid.uuid4().hex}.{file_extension}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Save uploaded file temporarily
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Processing meal image for user {current_user.id}: {temp_path}")
        
        # Analyze image with Azure AI
        analysis_result = azure_ai_service.analyze_food_image(temp_path)
        
        if not analysis_result:
            raise HTTPException(
                status_code=500,
                detail="Failed to analyze image. Please try again."
            )
        
        # Get user profile for personalized recommendations
        from app.models.user import UserProfile
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        # Prepare user data for personalized recommendations
        user_data = {}
        if user_profile:
            user_data = {
                'age': user_profile.age,
                'chronic_conditions': user_profile.chronic_conditions or [],
                'gender': user_profile.gender
            }
        
        # Get personalized health recommendation
        recommendation = azure_ai_service.get_health_recommendation(
            user_data, 
            analysis_result
        )
        
        # Calculate diet score based on analysis
        diet_score = calculate_diet_score(analysis_result, user_data)
        
        # Save to database
        food_log = FoodLog(
            user_id=current_user.id,
            meal_type=meal_type,
            food_image_url=temp_path,  # In production, upload to Azure Blob Storage
            ai_analysis=analysis_result,
            diet_score=diet_score,
            nutrients=analysis_result.get('nutrients', {}),
            created_at=datetime.now()
        )
        
        db.add(food_log)
        db.commit()
        db.refresh(food_log)
        
        # Prepare response
        response = {
            "analysis_id": food_log.id,
            "meal_type": meal_type,
            "detected_food": analysis_result.get('detected_food', 'Unknown'),
            "description": analysis_result.get('description', ''),
            "tags": analysis_result.get('tags', []),
            "nutrients": analysis_result.get('nutrients', {}),
            "confidence": analysis_result.get('confidence', 0),
            "diet_score": diet_score,
            "recommendation": recommendation,
            "analysis_source": analysis_result.get('analysis_source', 'azure_ai'),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Meal analysis completed for user {current_user.id}: {analysis_result.get('detected_food')}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing meal image: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass

@router.get("/recent-meals", response_model=list)
async def get_recent_meals(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's recent meal analyses"""
    
    meals = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id
    ).order_by(
        FoodLog.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    result = []
    for meal in meals:
        result.append({
            "id": meal.id,
            "meal_type": meal.meal_type,
            "detected_food": meal.ai_analysis.get('detected_food', 'Unknown') if meal.ai_analysis else 'Unknown',
            "diet_score": meal.diet_score,
            "nutrients": meal.nutrients or {},
            "created_at": meal.created_at.isoformat(),
            "recommendation": meal.ai_analysis.get('recommendation', '') if meal.ai_analysis else ''
        })
    
    return result

def calculate_diet_score(analysis_result: dict, user_data: dict) -> int:
    """Calculate a diet score from 0-100 based on analysis and user health"""
    
    base_score = 70  # Start with neutral score
    
    nutrients = analysis_result.get('nutrients', {})
    
    # Adjust based on nutritional values
    if nutrients.get('calories', 0) > 500:
        base_score -= 15
    elif nutrients.get('calories', 0) < 200:
        base_score += 10
    
    if nutrients.get('protein', 0) > 20:
        base_score += 10
    
    if nutrients.get('carbs', 0) > 60:
        base_score -= 10
    
    # Adjust based on user health conditions
    chronic_conditions = user_data.get('chronic_conditions', [])
    
    if 'diabetes' in chronic_conditions and nutrients.get('carbs', 0) > 40:
        base_score -= 20
    
    if 'hypertension' in chronic_conditions and nutrients.get('type') == 'high_sodium':
        base_score -= 15
    
    # Adjust based on food type
    food_type = nutrients.get('type', '')
    if food_type in ['vegetable', 'fruit']:
        base_score += 15
    elif food_type in ['starch', 'grain']:
        base_score -= 5
    
    # Ensure score is within bounds
    return max(0, min(100, base_score))

@router.post("/log-meal-manual")
async def log_meal_manual(
    meal_type: str,
    food_name: str,
    calories: int,
    carbs: int,
    protein: int,
    fats: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Manual meal logging (fallback when no image)"""
    
    # Create manual analysis
    analysis_result = {
        "detected_food": food_name,
        "description": f"Manually logged: {food_name}",
        "tags": ["manual_log", food_name.lower()],
        "nutrients": {
            "calories": calories,
            "carbs": carbs,
            "protein": protein,
            "fat": fats,
            "type": "manual_entry"
        },
        "confidence": 1.0,
        "analysis_source": "manual"
    }
    
    # Calculate score
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    user_data = {}
    if user_profile:
        user_data = {
            'age': user_profile.age,
            'chronic_conditions': user_profile.chronic_conditions or [],
            'gender': user_profile.gender
        }
    
    diet_score = calculate_diet_score(analysis_result, user_data)
    
    # Save to database
    food_log = FoodLog(
        user_id=current_user.id,
        meal_type=meal_type,
        ai_analysis=analysis_result,
        diet_score=diet_score,
        nutrients=analysis_result['nutrients'],
        created_at=datetime.now()
    )
    
    db.add(food_log)
    db.commit()
    
    return {
        "message": "Meal logged successfully",
        "meal_id": food_log.id,
        "food_name": food_name,
        "diet_score": diet_score
    }