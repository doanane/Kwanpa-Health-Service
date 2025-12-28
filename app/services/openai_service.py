import os
import requests
import json
from typing import Dict, Any, List
import logging
import re

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5-chat")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        
        
        if not self.endpoint or not self.api_key:
            logger.warning("Azure OpenAI credentials not found in environment variables")
    
    def analyze_food_for_chronic_disease(self, food_name: str, user_data: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive food analysis for chronic disease patients.
        Returns JSON analysis.
        """
        logger.info(f"Analyzing food for chronic disease: {food_name}")
        
        
        chronic_conditions = []
        if user_data and user_data.get('chronic_conditions'):
            conditions = user_data['chronic_conditions']
            if isinstance(conditions, list):
                chronic_conditions = conditions
            elif isinstance(conditions, str):
                try:
                    import ast
                    chronic_conditions = ast.literal_eval(conditions)
                except:
                    chronic_conditions = [conditions]
        
        
        conditions_text = ", ".join(chronic_conditions) if chronic_conditions else "general health maintenance"
        age = user_data.get('age', 'adult') if user_data else 'adult'
        
        
        prompt = f"""
        Analyze this Ghanaian food for a patient with chronic diseases.

        FOOD: {food_name}
        PATIENT: {age}-year-old ADULT with {conditions_text}

        Return a JSON OBJECT with the following keys. Do not use Markdown formatting.
        
        {{
            "description": "Briefly describe this traditional Ghanaian dish.",
            "nutrients": {{
                "calories": 0,
                "carbs": 0,
                "protein": 0,
                "fat": 0
            }},
            "chronic_disease_impact": "Explain impact on diabetes/hypertension/kidney disease for ADULTS. Simple terms.",
            "immediate_recommendation": "What should the ADULT patient do right now? Simple terms.",
            "portion_guidance": "How much should an ADULT eat?",
            "balancing_advice": "What to add/remove for better nutrition?",
            "healthier_alternative": "Suggest a better Ghanaian option for ADULTS.",
            "warning_level": "low, medium, or high",
            "key_nutrients_to_watch": ["nutrient1", "nutrient2"]
        }}
        """

        
        messages = [
            {
                "role": "system", 
                "content": "You are a Ghanaian clinical nutritionist. You MUST output valid JSON only."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            
            response_text = self._call_openai(messages, max_tokens=500)
            logger.info(f"OpenAI raw response: {response_text[:200]}...")
            
            
            try:
                parsed_data = json.loads(response_text)
            except json.JSONDecodeError:
                
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(clean_text)

            
            if "nutrients" not in parsed_data or not isinstance(parsed_data["nutrients"], dict):
                parsed_data["nutrients"] = {}

            
            parsed_data["is_balanced"] = self._is_food_balanced(food_name, chronic_conditions)
            parsed_data["diet_score"] = self._calculate_diet_score(parsed_data.get("nutrients", {}), chronic_conditions)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {str(e)}")
            return self._get_complete_fallback_analysis(food_name, chronic_conditions)
    
    def get_daily_health_tip(self, user_data: Dict = None) -> str:
        """Get personalized daily health tip"""
        
        chronic_conditions = []
        if user_data and user_data.get('chronic_conditions'):
            conditions = user_data['chronic_conditions']
            if isinstance(conditions, list):
                chronic_conditions = conditions
        
        prompt = f"""
        Give one specific daily health tip for managing {', '.join(chronic_conditions) if chronic_conditions else 'chronic conditions'} in Ghana.
        Make it practical, culturally appropriate, and include a specific action or measurement.
        Maximum 2 sentences. Plain text only.
        """
        
        messages = [
            {"role": "system", "content": "You are a helpful Ghanaian health advisor."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            
            return self._call_openai(messages, max_tokens=100, json_mode=False)
        except:
            return "Monitor your health regularly and take medications as prescribed."

    def _call_openai(self, messages: List[Dict], max_tokens: int = 500, json_mode: bool = True) -> str:
        """Call Azure OpenAI API"""
        if not self.endpoint or not self.api_key:
            raise Exception("Azure OpenAI credentials not configured")
        
        url = f"{self.endpoint}/openai/deployments/{self.deployment}/chat/completions"
        params = {"api-version": self.api_version}
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.5
        }

        
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            
            
            if response.status_code != 200:
                logger.error(f"OpenAI Error Body: {response.text}")
                
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise

    

    def _is_food_balanced(self, food_name: str, conditions: List[str]) -> bool:
        """Check if food is balanced for conditions"""
        food_lower = food_name.lower()
        
        
        if any('diabet' in str(c).lower() for c in conditions):
            if any(starch in food_lower for starch in ['rice', 'omotuo', 'banku', 'fufu', 'yam']):
                return False
        
        
        if any('hypertens' in str(c).lower() or 'blood pressure' in str(c).lower() for c in conditions):
            if 'soup' in food_lower or 'stew' in food_lower:
                return False
        
        return True
    
    def _calculate_diet_score(self, nutrients: Dict[str, Any], conditions: List[str]) -> int:
        """Calculate diet score 0-100"""
        base_score = 70
        
        
        calories = nutrients.get("calories", 300) or 300
        if 250 <= calories <= 400:
            base_score += 10
        elif calories > 500:
            base_score -= 15
        
        carbs = nutrients.get("carbs", 45) or 45
        if carbs < 60:
            base_score += 10
        elif carbs > 80:
            base_score -= 15
        
        protein = nutrients.get("protein", 12) or 12
        if protein >= 15:
            base_score += 10
        
        
        if any('diabet' in str(c).lower() for c in conditions) and carbs > 50:
            base_score -= 20
        
        if any('hypertens' in str(c).lower() for c in conditions):
            base_score += 5  
        
        return max(0, min(100, base_score))
    
    def _get_complete_fallback_analysis(self, food_name: str, conditions: List[str]) -> Dict[str, Any]:
        """Fallback analysis when OpenAI fails"""
        food_lower = food_name.lower()
        
        
        nutrients = {
            "calories": 300,
            "carbs": 45,
            "protein": 12,
            "fat": 10,
            "type": "unknown"
        }
        
        
        if 'omotuo' in food_lower or 'rice' in food_lower:
            nutrients = {"calories": 280, "carbs": 55, "protein": 8, "fat": 6, "type": "high_starch"}
            description = "Omotuo are soft rice balls, a traditional Ghanaian dish often served with soup."
            immediate = "Limit to ½ cup (1 small rice ball) to manage blood sugar."
            portion = "½ cup maximum. Use a measuring cup."
            balance = "Add vegetables and lean protein to slow glucose absorption."
            alternative = "Try brown rice or mix with cauliflower rice."
        else:
            description = f"A plate of {food_name.replace('_', ' ')}"
            immediate = "Enjoy in moderation as part of a balanced diet."
            portion = "Standard serving appropriate for your needs."
            balance = "Include vegetables and protein sources."
            alternative = "Consider healthier preparation methods."
        
        
        warning = "low"
        key_nutrients = ["calories", "protein"]
        
        if any('diabet' in str(c).lower() for c in conditions) and 'rice' in food_lower:
            warning = "high"
            key_nutrients = ["carbohydrates", "sugar"]
        elif any('hypertens' in str(c).lower() for c in conditions):
            warning = "medium"
            key_nutrients = ["sodium", "potassium"]
        
        return {
            "description": description,
            "nutrients": nutrients,
            "chronic_disease_impact": "Consult your healthcare provider for personalized advice.",
            "immediate_recommendation": immediate,
            "portion_guidance": portion,
            "balancing_advice": balance,
            "healthier_alternative": alternative,
            "warning_level": warning,
            "key_nutrients_to_watch": key_nutrients,
            "is_balanced": self._is_food_balanced(food_name, conditions),
            "diet_score": self._calculate_diet_score(nutrients, conditions)
        }