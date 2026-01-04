import os
import logging
from typing import Dict, Any, Optional
import requests
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from openai import AzureOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class AzureAIService:
    def __init__(self):
        self.vision_client = None
        self.openai_client = None
        
        # Initialize Azure Computer Vision (Legacy/Backup)
        if settings.AZURE_AI_VISION_ENDPOINT and settings.AZURE_AI_VISION_KEY:
            try:
                credentials = CognitiveServicesCredentials(settings.AZURE_AI_VISION_KEY)
                self.vision_client = ComputerVisionClient(
                    endpoint=settings.AZURE_AI_VISION_ENDPOINT,
                    credentials=credentials
                )
                logger.info("Azure AI Vision initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Vision: {e}")
        
        # Initialize Azure OpenAI
        if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
            try:
                self.openai_client = AzureOpenAI(
                    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                    api_key=settings.AZURE_OPENAI_KEY,
                    api_version="2024-02-01"
                )
                logger.info("Azure OpenAI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure OpenAI: {e}")
        else:
            logger.warning("Azure OpenAI credentials not configured")
    
    def analyze_food_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Analyze food image using Azure Custom Vision Prediction API"""
        if not settings.AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT or not settings.AZURE_CUSTOM_VISION_PREDICTION_KEY:
            logger.warning("Azure Custom Vision not configured, using mock analysis")
            return self._mock_food_analysis()
        
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Custom Vision Prediction API headers
            headers = {
                "Prediction-Key": settings.AZURE_CUSTOM_VISION_PREDICTION_KEY,
                "Content-Type": "application/octet-stream"
            }
            
            # Call Custom Vision Prediction API
            response = requests.post(
                settings.AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT,
                headers=headers,
                data=image_data
            )
            
            if response.status_code != 200:
                logger.error(f"Custom Vision API error: {response.status_code} - {response.text}")
                return self._mock_food_analysis()
            
            analysis_result = response.json()
            
            # Extract predictions
            predictions = analysis_result.get("predictions", [])
            if not predictions:
                logger.warning("No predictions returned from Custom Vision")
                return self._mock_food_analysis()
            
            # Get top prediction
            top_prediction = predictions[0]
            detected_food = top_prediction.get("tagName", "Unknown food")
            confidence = top_prediction.get("probability", 0)
            
            # Ghanaian food database
            ghanaian_foods = {
                "fufu": {"calories": 250, "carbs": 60, "protein": 5, "fat": 1, "type": "starch"},
                "banku": {"calories": 280, "carbs": 65, "protein": 6, "fat": 2, "type": "starch"},
                "kenkey": {"calories": 270, "carbs": 63, "protein": 5, "fat": 1, "type": "starch"},
                "jollof rice": {"calories": 200, "carbs": 45, "protein": 4, "fat": 5, "type": "grain"},
                "waakye": {"calories": 220, "carbs": 48, "protein": 8, "fat": 3, "type": "grain"},
                "tilapia": {"calories": 180, "carbs": 0, "protein": 35, "fat": 5, "type": "protein"},
                "plantain": {"calories": 120, "carbs": 31, "protein": 1, "fat": 0, "type": "fruit"},
                "kontomire stew": {"calories": 150, "carbs": 10, "protein": 8, "fat": 8, "type": "vegetable"},
                "red red": {"calories": 300, "carbs": 40, "protein": 12, "fat": 10, "type": "legume"},
            }
            
            # Match detected food with Ghanaian foods
            nutrients = None
            for food_name, food_info in ghanaian_foods.items():
                if food_name in detected_food.lower() or detected_food.lower() in food_name:
                    nutrients = food_info
                    break
            
            result = {
                "description": f"Detected {detected_food} with {confidence:.1%} confidence",
                "tags": [p.get("tagName") for p in predictions if p.get("probability", 0) > 0.3],
                "detected_food": detected_food,
                "nutrients": nutrients or {"calories": 200, "carbs": 40, "protein": 10, "fat": 5, "type": "unknown"},
                "confidence": confidence,
                "analysis_source": "azure_custom_vision"
            }
            
            logger.info(f"Custom Vision analysis completed: {detected_food} ({confidence:.1%})")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing food image with Custom Vision: {e}")
            return self._mock_food_analysis()
    
    def get_health_recommendation(self, user_data: Dict[str, Any], food_data: Dict[str, Any]) -> str:
        """Get personalized health recommendation using Azure OpenAI"""
        if not self.openai_client:
            logger.warning("Azure OpenAI not configured, using mock recommendation")
            return self._mock_recommendation(user_data, food_data)
        
        try:
            prompt = f"""
            You are HEWAL3, a Ghanaian health assistant specializing in chronic disease management.
            
            Patient Profile:
            - Age: {user_data.get('age', 'Unknown')}
            - Conditions: {', '.join(user_data.get('chronic_conditions', []))}
            - Recent food: {food_data.get('detected_food', 'Unknown')}
            - Food nutrients: {food_data.get('nutrients', {})}
            - Latest vitals: Heart rate: {user_data.get('heart_rate', 'Unknown')}, Blood pressure: {user_data.get('blood_pressure', 'Unknown')}
            
            Provide a personalized health recommendation in 2-3 sentences. Focus on:
            1. Ghanaian context and local foods
            2. Practical advice for managing their conditions
            3. Encouraging but honest feedback
            4. Suggestions for next meal if current food is problematic
            
            Response should be friendly, culturally appropriate, and medically sound.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",  # or your deployment name
                messages=[
                    {"role": "system", "content": "You are a helpful Ghanaian health assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            recommendation = response.choices[0].message.content.strip()
            logger.info(f"Generated recommendation: {recommendation[:50]}...")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting AI recommendation: {e}")
            return self._mock_recommendation(user_data, food_data)
    
    def _mock_food_analysis(self) -> Dict[str, Any]:
        """Mock food analysis for testing"""
        return {
            "description": "A plate of food",
            "tags": ["food", "plate", "meal"],
            "detected_food": "Sample Ghanaian Meal",
            "nutrients": {"calories": 250, "carbs": 50, "protein": 15, "fat": 8, "type": "balanced"},
            "confidence": 0.8,
            "analysis_source": "mock_service"
        }
    
    def _mock_recommendation(self, user_data: Dict[str, Any], food_data: Dict[str, Any]) -> str:
        """Mock recommendation for testing"""
        food_type = food_data.get('nutrients', {}).get('type', 'unknown')
        
        if food_type == "starch" and "diabetes" in user_data.get('chronic_conditions', []):
            return "This meal is high in starch. For better blood sugar control, consider reducing portion size and adding more leafy vegetables like kontomire."
        elif food_type == "protein":
            return "Good protein choice. Protein helps maintain muscle mass and keeps you full longer. Consider adding a side of vegetables for balanced nutrition."
        else:
            return "Your meal looks balanced. Remember to drink plenty of water and take your medications as prescribed."

# Singleton instance
azure_ai_service = AzureAIService()