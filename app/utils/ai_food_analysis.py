import os
import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class FoodAnalyzer:
    # UPDATED: Use the exact names from your .env file
    PREDICTION_ENDPOINT = os.getenv(
        "AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT")
    
    PREDICTION_KEY = os.getenv(
        "AZURE_CUSTOM_VISION_PREDICTION_KEY")
    
    # UPDATED: Add GEMINI_API_KEY
    GEMINI_API_KEY = os.getenv(
        "GEMINI_API")

    FOOD_CATEGORY_MAP = {
        "Tatale_Ghana": "high_starch",
        "Fufu_Ghana": "high_starch",
        "Waakye_Ghana": "balanced",
        "Kelewele_Ghana": "snack",
        "Banku_Ghana": "high_starch",
        "Light_soup_Ghana": "protein",
        "Jollof_rice_Ghana": "balanced",
        "Omotuo_Ghana": "high_starch",
        "Kontomire_stew_Ghana": "protein",
        "Kenkey_Ghana": "high_starch",
        "Groundnut_soup_Ghana": "protein",
        "Palm_nut_soup_Ghana": "protein",
        # ADD THIS: Map "Okro_Stew_Ghana" that your model returns
        "Okro_Stew_Ghana": "protein"  # New addition
    }

    @classmethod
    def analyze_food_image(cls, image_path: str) -> Dict[str, Any]:
        """
        Send image to Custom Vision Prediction API
        """
        # Log the credentials being used (remove in production)
        logger.info(f"Using endpoint: {cls.PREDICTION_ENDPOINT[:50]}...")
        logger.info(f"Using key: {cls.PREDICTION_KEY[:10]}...")
        
        # Validate endpoint and key
        if not cls.PREDICTION_ENDPOINT or not cls.PREDICTION_KEY:
            logger.error("Custom Vision credentials not configured")
            return cls._get_fallback_response("Service configuration error")
        
        headers = {
            "Prediction-Key": cls.PREDICTION_KEY,
            "Content-Type": "application/octet-stream"
        }

        try:
            # Read and send image
            with open(image_path, "rb") as image_data:
                response = requests.post(
                    cls.PREDICTION_ENDPOINT,
                    headers=headers,
                    data=image_data,
                    timeout=30
                )
                
                # Check response status
                if response.status_code != 200:
                    logger.error(f"Custom Vision API error: {response.status_code} - {response.text}")
                    return cls._get_fallback_response(f"API Error: {response.status_code}")
                
                result = response.json()
            
            # Log the full response for debugging
            logger.debug(f"Custom Vision raw response: {result}")
            
            # Check if we have predictions
            if "predictions" not in result or not result["predictions"]:
                logger.warning("No predictions returned from Custom Vision")
                return cls._get_fallback_response("No food detected in image")
            
            # Get top prediction
            predictions = result["predictions"]
            top_prediction = max(predictions, key=lambda x: x["probability"])
            
            food_label = top_prediction["tagName"]
            confidence = round(top_prediction["probability"] * 100, 2)
            
            logger.info(f"Custom Vision detected: {food_label} ({confidence}%)")
            
            # SPECIAL FIX: If it's Okro Stew but looks like Jollof Rice
            if food_label == "Okro_Stew_Ghana" and confidence < 70:
                # Try to check if it might be jollof rice
                # You could add image analysis here, but for now, guess based on name
                logger.info(f"Low confidence Okro Stew detected ({confidence}%). Checking if it might be jollof...")
                # Add this logic if you want to override
                if "rice" in food_label.lower() or "jollof" in food_label.lower():
                    food_label = "Jollof_rice_Ghana"
                    confidence = 65  # Set reasonable confidence
            
            # Map to category
            category = cls.FOOD_CATEGORY_MAP.get(food_label, "unknown")
            
            # If category is unknown but we recognize part of the name
            if category == "unknown":
                food_label = cls._guess_food_from_name(food_label)
                category = cls.FOOD_CATEGORY_MAP.get(food_label, "unknown")
            
            # Generate recommendations
            tips = cls._get_recommendations_for_category(category, food_label)
            
            return {
                "food": food_label,
                "category": category,
                "confidence": confidence,
                "analysis": "Food inference completed via Custom Vision",
                "recommendations": tips,
                "is_balanced": category == "balanced",
                "raw_tag": food_label  # Keep original for debugging
            }
            
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return cls._get_fallback_response("Image file not found")
        except requests.exceptions.Timeout:
            logger.error("Custom Vision request timeout")
            return cls._get_fallback_response("Service timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Custom Vision request failed: {str(e)}")
            return cls._get_fallback_response(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in analyze_food_image: {str(e)}")
            return cls._get_fallback_response(f"Analysis error: {str(e)}")
    
    @classmethod
    def _get_fallback_response(cls, error_message: str) -> Dict[str, Any]:
        """Create a fallback response when analysis fails"""
        return {
            "food": "Unknown",
            "category": "unknown",
            "confidence": 0,
            "analysis": error_message,
            "recommendations": ["Please try again with a clearer image", "Or use manual food logging"],
            "is_balanced": False
        }
    
    @classmethod
    def _guess_food_from_name(cls, food_label: str) -> str:
        """Try to guess actual food from similar names"""
        food_lower = food_label.lower()
        
        # Common misclassifications
        if "rice" in food_lower:
            return "Jollof_rice_Ghana"
        elif "soup" in food_lower and "light" in food_lower:
            return "Light_soup_Ghana"
        elif "soup" in food_lower and "groundnut" in food_lower:
            return "Groundnut_soup_Ghana"
        elif "ball" in food_lower or "rice ball" in food_lower:
            return "Omotuo_Ghana"
        elif "plantain" in food_lower:
            return "Kelewele_Ghana"
        elif "okro" in food_lower or "okra" in food_lower:
            return "Okro_Stew_Ghana"  # Map to newly added category
        
        return "Unknown"
    
    @classmethod
    def _get_recommendations_for_category(cls, category: str, food_name: str) -> list:
        """Get recommendations based on food category"""
        if category == "high_starch":
            return [
                f"{food_name} is high in starch. Balance with vegetables and protein.",
                "Consider reducing portion size if managing diabetes."
            ]
        elif category == "protein":
            return [
                f"{food_name} provides good protein.",
                "Pair with vegetables and whole grains for balanced nutrition."
            ]
        elif category == "balanced":
            return [
                f"{food_name} appears balanced.",
                "Maintain moderate portions for optimal health."
            ]
        elif category == "snack":
            return [
                f"{food_name} is a snack food.",
                "Enjoy in moderation as part of a balanced diet."
            ]
        else:
            return [
                f"{food_name} detected. Consult nutritionist for specific advice.",
                "Monitor portion sizes appropriate for your health conditions."
            ]
    
    @classmethod
    def get_daily_tip(cls, user_logs: dict) -> str:
        """
        Provide a daily health tip using Gemini (Google Generative AI) API.
        """
        try:
            import google.generativeai as genai
            # UPDATED: Use GEMINI_API_KEY from class attribute
            api_key = cls.GEMINI_API_KEY
            
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-pro")
                
                prompt = (
                    "Based on the following user health logs, provide a concise daily health tip for chronic disease management in Ghana:\n"
                    f"{user_logs}\nTip:"
                )
                
                response = model.generate_content(prompt)
                return response.text.strip()
        
        except Exception as e:
            logger.warning(f"Gemini API failed: {str(e)}")
        
        # Fallback to static tips
        static_tips = [
            "Stay hydrated! Drink at least 8 glasses of water daily.",
            "Include vegetables in every meal for better nutrition.",
            "Monitor your blood pressure regularly.",
            "Take medications as prescribed by your doctor.",
            "Get at least 30 minutes of exercise daily."
        ]
        
        import random
        return random.choice(static_tips)