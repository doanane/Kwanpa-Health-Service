from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
import os
from datetime import datetime
import tempfile
import logging
import json

from app.database import get_db
from app.auth.security import get_current_active_user
from app.models.user import User, UserProfile
from app.models.health import FoodLog
from app.services.azure_ai import azure_ai_service
from app.services.openai_service import OpenAIService

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
    """
    Analyze a meal image using Azure AI Vision and OpenAI.
    
    1. Identifies food using Azure Vision
    2. Generates detailed health analysis using OpenAI
    3. Saves to database
    """
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(400, f"Unsupported file type: {file.content_type}. Allowed: {', '.join(allowed_types)}")
    
    logger.info(f"Received file upload - Filename: {file.filename}, Content-Type: {file.content_type}")
    
    # Check size (10MB max) - with error handling for React Native uploads
    max_size = 10 * 1024 * 1024
    try:
        file.file.seek(0, 2)
        file_size = file.file.tell()
        if file_size > max_size:
            raise HTTPException(400, "File too large. Maximum size is 10MB")
        file.file.seek(0)
        logger.info(f"File size: {file_size} bytes")
    except Exception as e:
        logger.warning(f"Could not check file size: {e}. Proceeding anyway...")
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    temp_filename = f"meal_{uuid.uuid4().hex}.{file_extension}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Save file to disk - handle React Native uploads differently
        with open(temp_path, "wb") as buffer:
            try:
                content = await file.read()
                buffer.write(content)
                logger.info(f"✅ File saved successfully: {len(content)} bytes written to {temp_path}")
            except AttributeError as e:
                logger.error(f"❌ File read error (AttributeError): {e}")
                # Try alternative method for React Native
                try:
                    content = file.file.read()
                    buffer.write(content)
                    logger.info(f"✅ File saved using fallback method: {len(content)} bytes")
                except Exception as e2:
                    logger.error(f"❌ Fallback also failed: {e2}")
                    raise HTTPException(400, f"Failed to read uploaded file. Error: {str(e)}")
            except Exception as e:
                logger.error(f"❌ Unexpected file read error: {e}")
                raise HTTPException(400, f"Failed to process uploaded file: {str(e)}")
        
        logger.info(f"🔍 Processing meal image for user {current_user.id}: {temp_path}")
        
        # Step 1: Vision Analysis (Azure AI)
        vision_result = azure_ai_service.analyze_food_image(temp_path)
        
        if not vision_result:
            raise HTTPException(500, "Failed to analyze image. Please try again.")
            
        detected_food = vision_result.get("detected_food", "Unknown")
        confidence = vision_result.get("confidence", 0)
        
        # Step 2: Get User Profile
        user_profile = db.query(UserProfile).filter(
            UserProfile.user_id == current_user.id
        ).first()
        
        user_data = {}
        if user_profile:
            user_data = {
                'age': getattr(user_profile, 'age', None),
                'chronic_conditions': getattr(user_profile, 'chronic_conditions', []) or [],
                'gender': getattr(user_profile, 'gender', 'unknown')
            }
        
        # Step 3: Detailed Health Analysis (OpenAI)
        try:
            ai_analysis = openai_service.analyze_food_for_chronic_disease(detected_food, user_data)
            logger.info(f"OpenAI analysis completed for {detected_food}")
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            # Fallback
            ai_analysis = openai_service._get_complete_fallback_analysis(detected_food, 
                user_data.get('chronic_conditions', []))

        # Calculate diet score (using helper or from analysis)
        diet_score = ai_analysis.get("diet_score", 70)
        
        # Step 4: Prepare Response
        response = {
            "analysis_id": f"meal_{datetime.now().timestamp()}",
            "meal_type": meal_type,
            "detected_food": detected_food,
            "description": ai_analysis.get("description", f"A plate of {detected_food}"),
            "tags": vision_result.get("tags", []),
            "nutrients": ai_analysis.get("nutrients", {}),
            "confidence": confidence,
            "diet_score": diet_score,
            
            # Recommendations
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
            "category": vision_result.get("category", "unknown")
        }
        
        # Step 5: Save to Database
        food_log = FoodLog(
            user_id=current_user.id,
            meal_type=meal_type,
            food_image_url=temp_path, # Note: In prod, upload to blob storage
            ai_analysis=response,
            diet_score=diet_score,
            nutrients=response["nutrients"],
            created_at=datetime.now()
        )
        
        db.add(food_log)
        db.commit()
        db.refresh(food_log)
        
        response["analysis_id"] = food_log.id
        
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")
    finally:
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
            'chronic_conditions': getattr(user_profile, 'chronic_conditions', []) or [],
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
        import random
        tips = [
            "Drink at least 8 glasses of water today.",
            "Include vegetables in every meal.",
            "Take a 30-minute walk.",
            "Monitor your blood pressure.",
            "Take medications as prescribed."
        ]
        return {
            "success": True,
            "tip": random.choice(tips),
            "personalized": False,
            "timestamp": datetime.now().isoformat()
        }

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
        # Handle potential missing keys safely
        analysis = meal.ai_analysis or {}
        result.append({
            "id": meal.id,
            "meal_type": meal.meal_type,
            "detected_food": analysis.get('detected_food', 'Unknown'),
            "diet_score": meal.diet_score,
            "nutrients": meal.nutrients or {},
            "created_at": meal.created_at.isoformat(),
            "primary_recommendation": analysis.get('primary_recommendation', analysis.get('recommendation', ''))
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
    
    # Construct analysis result
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
    
    # Get user profile for scoring
    user_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()
    
    user_data = {}
    if user_profile:
        user_data = {
            'age': getattr(user_profile, 'age', None),
            'chronic_conditions': getattr(user_profile, 'chronic_conditions', []) or [],
            'gender': getattr(user_profile, 'gender', 'unknown')
        }
    
    # Calculate score
    diet_score = calculate_diet_score(analysis_result, user_data)
    analysis_result["diet_score"] = diet_score
    
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

def calculate_diet_score(analysis_result: dict, user_data: dict) -> int:
    """Calculate a diet score from 0-100 based on analysis and user health"""
    
    base_score = 70  
    
    nutrients = analysis_result.get('nutrients', {})
    
    if nutrients.get('calories', 0) > 500:
        base_score -= 15
    elif nutrients.get('calories', 0) < 200:
        base_score += 10
    
    if nutrients.get('protein', 0) > 20:
        base_score += 10
    
    if nutrients.get('carbs', 0) > 60:
        base_score -= 10
    
    chronic_conditions = user_data.get('chronic_conditions', [])
    
    # Check for diabetes
    if any('diabet' in str(c).lower() for c in chronic_conditions) and nutrients.get('carbs', 0) > 40:
        base_score -= 20
    
    # Check for hypertension
    if any('hypertens' in str(c).lower() for c in chronic_conditions) and nutrients.get('type') == 'high_sodium':
        base_score -= 15
    
    food_type = nutrients.get('type', '')
    if food_type in ['vegetable', 'fruit']:
        base_score += 15
    elif food_type in ['starch', 'grain']:
        base_score -= 5
    
    return max(0, min(100, base_score))