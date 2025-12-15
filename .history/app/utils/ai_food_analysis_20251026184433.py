import random
from typing import Dict, Any

class FoodAnalyzer:
    @staticmethod
    def analyze_food_image(image_path: str) -> Dict[str, Any]:
        """
        Simulate AI food analysis
        In production, integrate with actual ML model
        """
        # Mock analysis - replace with actual ML model
        food_categories = ["protein", "carbohydrates", "vegetables", "fruits", "dairy"]
        portions = {category: round(random.uniform(0.1, 1.0), 2) for category in food_categories}
        
        total = sum(portions.values())
        normalized_portions = {k: round(v/total * 100, 2) for k, v in portions.items()}
        
        # Calculate diet score based on balanced diet
        protein_score = min(normalized_portions["protein"] / 30 * 100, 100)
        carb_score = max(0, 100 - (normalized_portions["carbohydrates"] - 40) * 2)
        vegetable_score = min(normalized_portions["vegetables"] / 25 * 100, 100)
        
        overall_score = int((protein_score + carb_score + vegetable_score) / 3)
        
        # Generate tips
        tips = []
        if normalized_portions["carbohydrates"] > 50:
            tips.append("Try reducing carbohydrate intake")
        if normalized_portions["protein"] < 20:
            tips.append("Consider adding more protein sources")
        if normalized_portions["vegetables"] < 20:
            tips.append("Increase vegetable portions for better nutrition")
        
        return {
            "food_categories": normalized_portions,
            "diet_score": overall_score,
            "analysis": "AI analysis completed",
            "recommendations": tips,
            "is_balanced": overall_score > 70
        }
    
    @staticmethod
    def get_daily_tip() -> str:
        tips = [
            "Try reducing salt intake this week",
            "Increase your water consumption to 8 glasses daily",
            "Consider adding a 30-minute walk to your routine",
            "Include more leafy greens in your meals",
            "Monitor your sugar intake carefully",
            "Practice mindful eating habits",
            "Get at least 7-8 hours of sleep nightly"
        ]
        return random.choice(tips)