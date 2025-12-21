import os
import requests
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
        Comprehensive food analysis for chronic disease patients
        Returns complete analysis with recommendations, nutrients, and warnings
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
        
        
        conditions_text = ", ".join(chronic_conditions) if chronic_conditions else "chronic conditions"
        age = user_data.get('age', 'adult') if user_data else 'adult'
        
        
        prompt = f"""
        Analyze this Ghanaian food for a patient with chronic diseases.

        FOOD: {food_name}
        PATIENT: {age}-year-old ADULT with {conditions_text}

        Provide a COMPLETE analysis with these sections:

        DESCRIPTION: Briefly describe this traditional Ghanaian dish.
        NUTRIENT ANALYSIS: Estimate calories, carbs, protein, fat for a standard adult portion.
        CHRONIC DISEASE IMPACT: How does this food affect diabetes, hypertension, or kidney disease in ADULTS?
        IMMEDIATE RECOMMENDATION: What should the ADULT patient do right now?
        PORTION GUIDANCE: How much should an ADULT eat?
        BALANCING ADVICE: What to add/remove for better nutrition?
        HEALTHIER ALTERNATIVE: Suggest a better Ghanaian option for ADULTS.
        WARNING LEVEL: low, medium, or high risk for their conditions.
        KEY NUTRIENTS TO WATCH: List 2-3 nutrients to monitor.

        CRITICAL INSTRUCTIONS:
        1. DO NOT use numbers (1., 2., 3., etc.) in your response
        2. DO NOT mention children, babies, or infants
        3. Focus on ADULT patients only
        4. Use plain sentences without numbering
        5. Each section should be 1-2 complete sentences
        """

        
        messages = [
            {
                "role": "system", 
                "content": "You are a Ghanaian clinical nutritionist analyzing traditional foods for ADULT patients with diabetes, hypertension, and kidney disease. Provide clear, practical advice for ADULTS only. Never mention children, babies, or infants. Do not use numbered lists or bullet points in your response."
            },
            {"role": "user", "content": prompt}
        ]
        
        try:
            
            response_text = self._call_openai(messages, max_tokens=400)
            logger.info(f"OpenAI raw response: {response_text[:200]}...")
            
            
            parsed_data = self._parse_complete_analysis(response_text)
            
            
            parsed_data["is_balanced"] = self._is_food_balanced(food_name, chronic_conditions)
            parsed_data["diet_score"] = self._calculate_diet_score(parsed_data.get("nutrients", {}), chronic_conditions)
            
            
            parsed_data = self._clean_all_text_fields(parsed_data)
            
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
            tip = self._call_openai(messages, max_tokens=100)
            return self._clean_text(tip)
        except:
            return "Monitor your health regularly and take medications as prescribed."
    
    def _parse_complete_analysis(self, text: str) -> Dict[str, Any]:
        """Parse the complete analysis from OpenAI response"""
        sections = {
            "description": "",
            "nutrients": {},
            "chronic_disease_impact": "",
            "immediate_recommendation": "",
            "portion_guidance": "",
            "balancing_advice": "",
            "healthier_alternative": "",
            "warning_level": "low",
            "key_nutrients_to_watch": []
        }
        
        current_section = None
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            
            if "DESCRIPTION:" in line.upper():
                current_section = "description"
                line = line.replace("DESCRIPTION:", "").strip()
            elif "NUTRIENT ANALYSIS:" in line.upper() or "NUTRIENTS:" in line.upper():
                current_section = "nutrients"
                line = line.replace("NUTRIENT ANALYSIS:", "").replace("NUTRIENTS:", "").strip()
            elif "CHRONIC DISEASE IMPACT:" in line.upper():
                current_section = "chronic_disease_impact"
                line = line.replace("CHRONIC DISEASE IMPACT:", "").strip()
            elif "IMMEDIATE RECOMMENDATION:" in line.upper():
                current_section = "immediate_recommendation"
                line = line.replace("IMMEDIATE RECOMMENDATION:", "").strip()
            elif "PORTION GUIDANCE:" in line.upper():
                current_section = "portion_guidance"
                line = line.replace("PORTION GUIDANCE:", "").strip()
            elif "BALANCING ADVICE:" in line.upper():
                current_section = "balancing_advice"
                line = line.replace("BALANCING ADVICE:", "").strip()
            elif "HEALTHIER ALTERNATIVE:" in line.upper():
                current_section = "healthier_alternative"
                line = line.replace("HEALTHIER ALTERNATIVE:", "").strip()
            elif "WARNING LEVEL:" in line.upper():
                current_section = "warning_level"
                line = line.replace("WARNING LEVEL:", "").strip().lower()
            elif "KEY NUTRIENTS TO WATCH:" in line.upper():
                current_section = "key_nutrients_to_watch"
                line = line.replace("KEY NUTRIENTS TO WATCH:", "").strip()
            
            
            if current_section and line:
                if current_section == "nutrients":
                    
                    nutrients = self._extract_nutrients_from_text(line)
                    if nutrients:
                        sections["nutrients"] = nutrients
                elif current_section == "key_nutrients_to_watch":
                    
                    nutrients = [n.strip() for n in re.split(',|;|and', line) if n.strip()]
                    sections["key_nutrients_to_watch"] = nutrients
                elif current_section == "warning_level":
                    if "high" in line.lower():
                        sections["warning_level"] = "high"
                    elif "medium" in line.lower():
                        sections["warning_level"] = "medium"
                    else:
                        sections["warning_level"] = "low"
                else:
                    if sections[current_section]:
                        sections[current_section] += " " + line
                    else:
                        sections[current_section] = line
        
        return sections
    
    def _extract_nutrients_from_text(self, text: str) -> Dict[str, Any]:
        """Extract nutrient values from text"""
        nutrients = {
            "calories": 300,
            "carbs": 45,
            "protein": 12,
            "fat": 10,
            "type": "unknown"
        }
        
        
        import re
        numbers = re.findall(r'\b(\d+)\s*(calories?|kcal|carbs?|carbohydrates?|protein|fat|g\b)', text.lower())
        
        for num, unit in numbers:
            num = int(num)
            if 'calori' in unit or 'kcal' in unit:
                nutrients["calories"] = num
            elif 'carb' in unit:
                nutrients["carbs"] = num
            elif 'protein' in unit:
                nutrients["protein"] = num
            elif 'fat' in unit:
                nutrients["fat"] = num
        
        return nutrients
    
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
        
        
        calories = nutrients.get("calories", 300)
        if 250 <= calories <= 400:
            base_score += 10
        elif calories > 500:
            base_score -= 15
        
        carbs = nutrients.get("carbs", 45)
        if carbs < 60:
            base_score += 10
        elif carbs > 80:
            base_score -= 15
        
        protein = nutrients.get("protein", 12)
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
    
    def _clean_all_text_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean all text fields in the response"""
        cleaned = {}
        for key, value in data.items():
            if isinstance(value, str):
                cleaned[key] = self._clean_text(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_text(str(item)) if isinstance(item, str) else item for item in value]
            elif isinstance(value, dict):
                cleaned[key] = self._clean_all_text_fields(value)
            else:
                cleaned[key] = value
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Remove all markdown and formatting"""
        if not text:
            return text
        
        
        text = re.sub(r'[\*\#\`\[\]\(\)]', '', text)
        
        
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 300) -> str:
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
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, params=params, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise