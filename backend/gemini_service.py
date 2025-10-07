"""
Gemini 2.5 Flash Integration for AI Diet and Workout Recommendations
Replaces traditional ML models with Gemini API for more flexible predictions
"""

import google.generativeai as genai
import json
import os
import logging
from typing import Dict, Any, List
from backend.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiRecommendationService:
    """
    Service class for generating recommendations using Gemini 2.5 Flash
    Replaces the traditional ML models with AI-powered recommendations
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.model = None
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Initialize Gemini API"""
        try:
            # Get API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.warning("GEMINI_API_KEY not found. Please set it in your environment variables.")
                return False
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini 2.5 Flash initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            return False
    
    def generate_diet_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized diet plan using Gemini
        """
        if not self.model:
            return self._fallback_diet_plan(user_data)
        
        try:
            # Calculate basic metrics
            bmi = user_data['weight'] / ((user_data['height'] / 100) ** 2)
            
            # Create detailed prompt for Gemini
            prompt = f"""
            You are a professional nutritionist and dietitian. Generate a personalized diet plan based on the following user profile:

            User Profile:
            - Age: {user_data['age']} years
            - Gender: {user_data['gender']}
            - Height: {user_data['height']} cm
            - Weight: {user_data['weight']} kg
            - BMI: {bmi:.1f}
            - Goal: {user_data['goal']}
            - Diet Preference: {user_data['diet_preference']}
            - Activity Level: {user_data['activity_level']}

            Please generate a comprehensive diet plan that includes:
            1. Daily calorie target
            2. Macro distribution (protein, carbs, fat)
            3. Three main meals (breakfast, lunch, dinner) with specific food items
            4. Each food item should include calories, protein, carbs, and fat content
            5. Meal timing recommendations
            6. Hydration goals

            Format the response as a JSON object with this structure:
            {{
                "target_calories": number,
                "macros": {{
                    "protein": number,
                    "carbs": number,
                    "fat": number
                }},
                "meal_plan": {{
                    "breakfast": {{
                        "name": "string",
                        "calories": number,
                        "protein": number,
                        "carbs": number,
                        "fat": number,
                        "time": "string"
                    }},
                    "lunch": {{
                        "name": "string",
                        "calories": number,
                        "protein": number,
                        "carbs": number,
                        "fat": number,
                        "time": "string"
                    }},
                    "dinner": {{
                        "name": "string",
                        "calories": number,
                        "protein": number,
                        "carbs": number,
                        "fat": number,
                        "time": "string"
                    }}
                }},
                "recommendations": "string"
            }}

            Make sure the total calories match the target and the macros are appropriate for the user's goal.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            diet_plan = self._parse_gemini_response(response.text)
            
            logger.info("✅ Diet plan generated successfully using Gemini")
            return diet_plan
            
        except Exception as e:
            logger.error(f"Error generating diet plan with Gemini: {e}")
            return self._fallback_diet_plan(user_data)
    
    def generate_workout_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized workout plan using Gemini
        """
        if not self.model:
            return self._fallback_workout_plan(user_data)
        
        try:
            prompt = f"""
            You are a certified personal trainer and fitness expert. Generate a personalized workout plan based on the following user profile:

            User Profile:
            - Age: {user_data['age']} years
            - Gender: {user_data['gender']}
            - Height: {user_data['height']} cm
            - Weight: {user_data['weight']} kg
            - Goal: {user_data['goal']}
            - Activity Level: {user_data['activity_level']}
            - Available Time: {user_data['workout_time']} minutes per day

            Please generate a comprehensive workout plan that includes:
            1. Workout name and description
            2. List of exercises with sets, reps, and duration
            3. Estimated calories burned
            4. Difficulty level appropriate for the user
            5. Equipment needed (prefer bodyweight exercises)
            6. Rest periods between exercises
            7. Progression tips

            Format the response as a JSON object with this structure:
            {{
                "name": "string",
                "description": "string",
                "duration": number,
                "difficulty": "string",
                "estimated_calories": number,
                "exercises": [
                    {{
                        "name": "string",
                        "sets": number,
                        "reps": "string",
                        "duration": number,
                        "calories": number,
                        "instructions": "string",
                        "muscle_groups": ["string"]
                    }}
                ],
                "equipment_needed": ["string"],
                "tips": "string"
            }}

            Make sure the workout is appropriate for the user's fitness level and time constraints.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            workout_plan = self._parse_gemini_response(response.text)
            
            logger.info("✅ Workout plan generated successfully using Gemini")
            return workout_plan
            
        except Exception as e:
            logger.error(f"Error generating workout plan with Gemini: {e}")
            return self._fallback_workout_plan(user_data)
    
    def generate_workout_plan_from_prompt(self, prompt: str) -> str:
        """
        Generate workout plan from a custom prompt string
        Returns JSON string response
        """
        if not self.model:
            return self._fallback_workout_plan_string()
        
        try:
            response = self.model.generate_content(prompt)
            logger.info("✅ Custom workout plan generated successfully using Gemini")
            
            # Clean the response - remove markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith('```'):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove trailing ```
            
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error generating custom workout plan with Gemini: {e}")
            return self._fallback_workout_plan_string()
    
    def _fallback_workout_plan_string(self) -> str:
        """Fallback workout plan as JSON string"""
        fallback_plan = {
            "workout_name": "Basic Full Body Workout",
            "exercises": [
                {
                    "name": "Push-ups",
                    "sets": 3,
                    "reps": "10-12",
                    "duration": 5,
                    "calories": 50,
                    "instructions": "Start in plank position, lower chest to ground, push back up",
                    "muscle_groups": ["Chest", "Triceps", "Shoulders"]
                },
                {
                    "name": "Squats",
                    "sets": 3,
                    "reps": "15-20",
                    "duration": 5,
                    "calories": 60,
                    "instructions": "Feet shoulder-width apart, lower hips back and down, return to standing",
                    "muscle_groups": ["Legs", "Glutes"]
                },
                {
                    "name": "Plank",
                    "sets": 3,
                    "reps": "30-60 seconds",
                    "duration": 3,
                    "calories": 30,
                    "instructions": "Hold body straight from head to heels, engage core muscles",
                    "muscle_groups": ["Core"]
                }
            ],
            "total_duration": 30,
            "total_calories": 140
        }
        return json.dumps(fallback_plan)
    
    def predict_calories_burned(self, user_data: Dict[str, Any], workout_data: Dict[str, Any]) -> int:
        """
        Predict calories burned for a specific workout using Gemini
        """
        if not self.model:
            return self._fallback_calorie_prediction(user_data, workout_data)
        
        try:
            prompt = f"""
            You are a fitness expert with expertise in calorie burn calculations. Calculate the estimated calories burned for this workout:

            User Profile:
            - Age: {user_data['age']} years
            - Gender: {user_data['gender']}
            - Weight: {user_data['weight']} kg

            Workout Details:
            - Type: {workout_data['type']}
            - Intensity: {workout_data['intensity']}
            - Duration: {workout_data['duration']} minutes

            Please provide:
            1. Estimated calories burned (as a single number)
            2. Brief explanation of the calculation method
            3. Factors that influenced the calculation

            Format the response as a JSON object:
            {{
                "calories_burned": number,
                "explanation": "string",
                "factors": ["string"]
            }}

            Use standard MET (Metabolic Equivalent of Task) values and consider the user's weight, age, and gender.
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse the response
            result = self._parse_gemini_response(response.text)
            
            logger.info("✅ Calorie prediction generated successfully using Gemini")
            return result.get('calories_burned', 100)
            
        except Exception as e:
            logger.error(f"Error predicting calories with Gemini: {e}")
            return self._fallback_calorie_prediction(user_data, workout_data)
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse Gemini response and extract JSON
        """
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in Gemini response")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return {}
    
    def _fallback_diet_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback diet plan when Gemini is not available"""
        logger.warning("Using fallback diet plan")
        
        # Calculate basic calories
        if user_data['gender'] == 'male':
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + 5
        else:
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] - 161
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'intense': 1.725
        }
        
        daily_calories = bmr * activity_multipliers.get(user_data['activity_level'], 1.55)
        
        goal_adjustments = {
            'weight-loss': 0.8,
            'maintenance': 1.0,
            'muscle-gain': 1.2
        }
        
        target_calories = int(daily_calories * goal_adjustments.get(user_data['goal'], 1.0))
        
        return {
            "target_calories": target_calories,
            "macros": {
                "protein": int(target_calories * 0.25 / 4),
                "carbs": int(target_calories * 0.45 / 4),
                "fat": int(target_calories * 0.30 / 9)
            },
            "meal_plan": {
                "breakfast": {
                    "name": "Balanced Breakfast",
                    "calories": int(target_calories * 0.25),
                    "protein": int(target_calories * 0.25 * 0.25 / 4),
                    "carbs": int(target_calories * 0.25 * 0.45 / 4),
                    "fat": int(target_calories * 0.25 * 0.30 / 9),
                    "time": "8:00 AM"
                },
                "lunch": {
                    "name": "Nutritious Lunch",
                    "calories": int(target_calories * 0.35),
                    "protein": int(target_calories * 0.35 * 0.25 / 4),
                    "carbs": int(target_calories * 0.35 * 0.45 / 4),
                    "fat": int(target_calories * 0.35 * 0.30 / 9),
                    "time": "1:00 PM"
                },
                "dinner": {
                    "name": "Light Dinner",
                    "calories": int(target_calories * 0.40),
                    "protein": int(target_calories * 0.40 * 0.25 / 4),
                    "carbs": int(target_calories * 0.40 * 0.45 / 4),
                    "fat": int(target_calories * 0.40 * 0.30 / 9),
                    "time": "7:00 PM"
                }
            },
            "recommendations": "Please consult with a nutritionist for personalized advice."
        }
    
    def _fallback_workout_plan(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback workout plan when Gemini is not available"""
        logger.warning("Using fallback workout plan")
        
        return {
            "name": "Basic Full Body Workout",
            "description": "A balanced workout for all fitness levels",
            "duration": 30,
            "difficulty": "beginner",
            "estimated_calories": 200,
            "exercises": [
                {
                    "name": "Push-ups",
                    "sets": 3,
                    "reps": "10-15",
                    "duration": 5,
                    "calories": 50,
                    "instructions": "Keep your body straight, lower chest to ground, push back up",
                    "muscle_groups": ["chest", "triceps"]
                },
                {
                    "name": "Squats",
                    "sets": 3,
                    "reps": "15-20",
                    "duration": 5,
                    "calories": 60,
                    "instructions": "Feet shoulder-width apart, lower hips back and down",
                    "muscle_groups": ["legs", "glutes"]
                },
                {
                    "name": "Plank",
                    "sets": 3,
                    "reps": "30 seconds",
                    "duration": 3,
                    "calories": 30,
                    "instructions": "Hold body straight from head to heels",
                    "muscle_groups": ["core"]
                }
            ],
            "equipment_needed": ["none"],
            "tips": "Focus on proper form over speed"
        }
    
    def _fallback_calorie_prediction(self, user_data: Dict[str, Any], workout_data: Dict[str, Any]) -> int:
        """Fallback calorie prediction when Gemini is not available"""
        logger.warning("Using fallback calorie prediction")
        
        # Basic MET calculation
        met_values = {
            ('strength', 'low'): 3.0,
            ('strength', 'moderate'): 5.0,
            ('strength', 'high'): 8.0,
            ('cardio', 'low'): 4.0,
            ('cardio', 'moderate'): 7.0,
            ('cardio', 'high'): 11.0,
            ('mixed', 'low'): 3.5,
            ('mixed', 'moderate'): 6.0,
            ('mixed', 'high'): 9.5
        }
        
        met = met_values.get((workout_data['type'], workout_data['intensity']), 5.0)
        calories = met * user_data['weight'] * (workout_data['duration'] / 60)
        
        # Gender adjustment
        if user_data['gender'] == 'male':
            calories *= 1.1
        else:
            calories *= 0.9
        
        return max(int(calories), 10)
