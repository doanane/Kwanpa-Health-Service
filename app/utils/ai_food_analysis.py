import requests, openai
import random
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()
class FoodAnalyzer:
    FOOD_CATEGORY_MAP = {
        "Tatale_Ghana": "high_starch",
        "Fufu_Ghana": "high_starch",
        "Waakye_Ghana": "balanced",
        "Kelewele_Ghana": "snack",
        "Banku_Ghana": "high_starch",
        "Light_soup_Ghana": "protein",
        "Jollof_rice_Ghana": "balanced"
    }

    PREDICTION_ENDPOINT = os.getenv("AZURE_CUSTOM_VISION_PREDICTION_ENDPOINT")

    PREDICTION_KEY =os.getenv("AZURE_CUSTOM_VISION_PREDICTION_KEY")
    @staticmethod
    def analyze_food_image(image_path: str) -> Dict[str, Any]:
        """
        Send image to Custom Vision Prediction API,
        map predicted food label to category, and return analysis with tips.
        """
        headers = {
            "Prediction-Key": FoodAnalyzer.PREDICTION_KEY,
            "Content-Type": "application/octet-stream"
        }

        with open(image_path, "rb") as image_data:
            response = requests.post(
                FoodAnalyzer.PREDICTION_ENDPOINT,
                headers=headers,
                data=image_data
            )
            result = response.json()

        # Extract top prediction
        top_prediction = max(result["predictions"], key=lambda x: x["probability"])
        food_label = top_prediction["tagName"]
        confidence = round(top_prediction["probability"] * 100, 2)

        # Map to category
        category = FoodAnalyzer.FOOD_CATEGORY_MAP.get(food_label, "unknown")

        # Generate recommendations based on category
        tips = []
        if category == "high_starch":
            tips.append("Balance high starch meals with more vegetables and protein.")
        elif category == "protein":
            tips.append("Good protein intake — add vegetables for balance.")
        elif category == "balanced":
            tips.append("This looks balanced — keep portions moderate.")
        elif category == "snack":
            tips.append("Snacks are fine occasionally, but keep portions moderate.")

        return {
            "food": food_label,
            "category": category,
            "confidence": confidence,
            "analysis": "Food inference completed via Custom Vision",
            "recommendations": tips,
            "is_balanced": category == "balanced"
        }

    @staticmethod
    def get_daily_tip_openai(user_logs: dict) -> str:
        """
        Provide a daily health tip using OpenAI API.
        Input: user_logs (dict with relevant health data)
        Process: Send user logs to OpenAI, get a personalized tip. 
        IDEAL-TOOL: Self Hosted GPT4 model on Azure OpenAI Service
        Output: Health tip string
        
        TODO: verify and setup system to provide ideal/sample user_logs.
                user_logs = {
                "age": 35,
                "gender": "male",
                "steps_today": 5000,
                "sleep_hours": 6,
                "meals": ["Fufu_Ghana", "Light_soup_Ghana"],
                "health_conditions": ["hypertension"],
                "water_intake": 5,
                "recent_symptoms": ["headache"]
            }
        """
        
        openai.api_key ="INPUT_KEY" #move to env
        
        prompt = (
            "Based on the following user health logs, provide a concise daily health tip for chronic disease management in Ghana:\n"
            f"{user_logs}\nTip:"
        )
        response = model.generate_content(prompt)
        tip = response.text.strip()
        return tip

    @staticmethod
    def get_daily_tip(user_logs: dict) -> str:
        """
        Provide a daily health tip using Gemini (Google Generative AI) API.
        Input: user_logs (dict with relevant health data)
        Process: Send user logs to Gemini, get a personalized tip.
        Output: Health tip string
        """
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API")
        
        if not api_key:
            raise RuntimeError("GEMINI_API is not set in the .env file")

            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            "Based on the following user health logs, provide a concise daily health tip for chronic disease management in Ghana:\n"
            f"{user_logs}\nTip:"
        )
        response = model.generate_content(prompt)
        tip = response.text.strip()
        return tip

# # Run inference
# result = FoodAnalyzer.analyze_food_image("/path/to/test_img.jpg")
# print(result)

# # Get a daily tip
# print(FoodAnalyzer.get_daily_tip())