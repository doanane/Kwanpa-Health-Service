from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import os
from datetime import datetime
import tempfile
import logging

from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User, UserProfile
from app.models.health import FoodLog
from app.utils.ai_food_analysis import FoodAnalyzer
from app.services.openai_service import OpenAIService
import json

logger = logging.getLogger(__name__)

# Initialize services
openai_service = OpenAIService()
router = APIRouter(prefix="/api", tags=["food_analysis"])

@router.post("/analyze-meal", response_model=dict)
async def analyze_meal(
    meal_type: str = Form(..., description="Type of meal: breakfast, lunch, dinner, snack"),
    file: UploadFile = File(..., description="Image of the meal"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze a meal image using Custom Vision and OpenAI"""
    
    # Validate file
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(allowed_types)}")
    
    # Check size (10MB max)
    max_size = 10 * 1024 * 1024
    file.file.seek(0, 2)
    if file.file.tell() > max_size:
        raise HTTPException(400, "File too large. Maximum size is 10MB")
    file.file.seek(0)
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    temp_filename = f"meal_{uuid.uuid4().hex}.{file_extension}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Save file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Processing meal image for user {current_user.id}")
        

        try:
            vision_result = FoodAnalyzer.analyze_food_image(temp_path)
            detected_food = vision_result.get("food", "Unknown")
            confidence = vision_result.get("confidence", 0)
            
            # If food is "Unknown" or confidence is too low, try fallback
            if detected_food == "Unknown" or confidence < 40:
                logger.warning(f"Custom Vision returned Unknown ({confidence}%). Trying fallback...")
                
                # Try to guess from image features
                try:
                    guessed_food = FoodAnalyzer.guess_food_from_image_features(temp_path)
                    if guessed_food != "Unknown":
                        detected_food = guessed_food
                        confidence = 50  # Set medium confidence for guess
                        logger.info(f"Image analysis guessed: {detected_food}")
                except Exception as guess_error:
                    logger.error(f"Image guess failed: {str(guess_error)}")
            
            # If still unknown, ask user
            if detected_food == "Unknown" or detected_food == "Unknown_Ghanaian_food":
                # You could return an error asking for manual input
                raise HTTPException(
                    status_code=400,
                    detail="Could not identify the food. Please: 1) Upload a clearer image, or 2) Use the manual log feature"
                )
            
            category = vision_result.get("category", "unknown")
            logger.info(f"Food detected: {detected_food} ({confidence}%)")
            
        except Exception as e:
            logger.error(f"Food detection failed: {str(e)}")
            raise HTTPException(500, "Food identification failed. Please try again or use manual logging.")
        
        # Step 2: Get user profile for personalized analysis
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        user_data = {}
        if user_profile:
            user_data = {
                'age': getattr(user_profile, 'age', None),
                'chronic_conditions': getattr(user_profile, 'chronic_conditions', []),
                'gender': getattr(user_profile, 'gender', 'unknown')
            }
        
        # Step 3: Get comprehensive analysis from OpenAI
        try:
            ai_analysis = openai_service.analyze_food_for_chronic_disease(detected_food, user_data)
            logger.info(f"OpenAI analysis completed for {detected_food}")
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            # Use fallback analysis
            ai_analysis = openai_service._get_complete_fallback_analysis(detected_food, 
                user_data.get('chronic_conditions', []))
        
        # Step 4: Prepare response
        response = {
            "analysis_id": f"meal_{datetime.now().timestamp()}",
            "meal_type": meal_type,
            "detected_food": detected_food,
            "description": ai_analysis.get("description", f"A plate of {detected_food.replace('_', ' ')}"),
            "tags": [category, detected_food.replace('_', ' ').lower()],
            "nutrients": ai_analysis.get("nutrients", {}),
            "confidence": confidence,
            "diet_score": ai_analysis.get("diet_score", 70),
            
            # Recommendations from OpenAI
            "primary_recommendation": ai_analysis.get("immediate_recommendation", ""),
            "secondary_recommendation": ai_analysis.get("balancing_advice", ""),
            
            # Detailed analysis
            "detailed_analysis": {
                "chronic_disease_impact": ai_analysis.get("chronic_disease_impact", ""),
                "portion_guidance": ai_analysis.get("portion_guidance", ""),
                "healthier_alternative": ai_analysis.get("healthier_alternative", ""),
                "warning_level": ai_analysis.get("warning_level", "low"),
                "key_nutrients_to_watch": ai_analysis.get("key_nutrients_to_watch", [])
            },
            
            "is_balanced": ai_analysis.get("is_balanced", True),
            "analysis_source": "azure_custom_vision + azure_openai",
            "timestamp": datetime.now().isoformat(),
            "category": category
        }
        
        # Step 5: Save to database
        food_log = FoodLog(
            user_id=current_user.id,
            meal_type=meal_type,
            food_image_url=temp_path,
            ai_analysis=response,
            diet_score=response["diet_score"],
            nutrients=response["nutrients"],
            created_at=datetime.now()
        )
        
        db.add(food_log)
        db.commit()
        db.refresh(food_log)
        response["analysis_id"] = food_log.id
        
        logger.info(f"✅ Analysis completed for user {current_user.id}: {detected_food}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")
    finally:
        # Clean up temp file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass

@router.get("/daily-tip")
async def get_daily_tip(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized daily health tip"""
    
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    user_data = {}
    if user_profile:
        user_data = {
            'age': getattr(user_profile, 'age', None),
            'chronic_conditions': getattr(user_profile, 'chronic_conditions', []),
            'gender': getattr(user_profile, 'gender', 'unknown')
        }
    
    try:
        tip = openai_service.get_daily_health_tip(user_data)
        return {
            "success": True,
            "tip": tip,
            "personalized": bool(user_data.get('chronic_conditions')),
            "timestamp": datetime.now().isoformat()
        }
    except:
        # Fallback tips
        import random
        tips = [
            "Drink at least 8 glasses of water today to stay hydrated.",
            "Include vegetables in every meal for better nutrition.",
            "Take a 30-minute walk to support heart health.",
            "Monitor your blood pressure regularly.",
            "Take medications as prescribed by your doctor."
        ]
        return {
            "success": True,
            "tip": random.choice(tips),
            "personalized": False,
            "timestamp": datetime.now().isoformat()
        }

# Keep other endpoints (recent-meals, log-meal-manual) as they were
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
    ).order_by(FoodLog.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for meal in meals:
        result.append({
            "id": meal.id,
            "meal_type": meal.meal_type,
            "detected_food": meal.ai_analysis.get('detected_food', 'Unknown') if meal.ai_analysis else 'Unknown',
            "diet_score": meal.diet_score,
            "nutrients": meal.nutrients or {},
            "created_at": meal.created_at.isoformat(),
            "primary_recommendation": meal.ai_analysis.get('primary_recommendation', '') if meal.ai_analysis else ''
        })
    
    return result

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
    """Manual meal logging"""
    food_log = FoodLog(
        user_id=current_user.id,
        meal_type=meal_type,
        ai_analysis={"food": food_name, "source": "manual"},
        diet_score=70,
        nutrients={"calories": calories, "carbs": carbs, "protein": protein, "fat": fats},
        created_at=datetime.now()
    )
    
    db.add(food_log)
    db.commit()
    
    return {
        "message": "Meal logged successfully",
        "meal_id": food_log.id,
        "food_name": food_name
    }