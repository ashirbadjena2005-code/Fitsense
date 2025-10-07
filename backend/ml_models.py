"""
AI-Powered Diet and Workout Recommendation System - ML Models
VS Code optimized version with Gemini 2.5 Flash integration
"""

import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sklearn.cluster import KMeans
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json

# Import configuration and Gemini service
from backend.config import get_config
from backend.gemini_service import GeminiRecommendationService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DietRecommendationSystem:
    """
    Gemini 2.5 Flash powered diet recommendation system
    Replaces traditional ML models with AI-powered recommendations
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.gemini_service = GeminiRecommendationService(config)
        
        # Keep fallback models for when Gemini is not available
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.decision_tree = DecisionTreeClassifier(random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Ensure models directory exists
        os.makedirs(self.config.MODELS_PATH, exist_ok=True)
        
    def prepare_sample_data(self):
        """Generate sample user data for training"""
        logger.info("Generating sample training data...")
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'weight': np.random.normal(70, 15, n_samples),
            'height': np.random.normal(170, 10, n_samples),
            'gender': np.random.choice(['male', 'female'], n_samples),
            'activity_level': np.random.choice(['sedentary', 'light', 'moderate', 'intense'], n_samples),
            'goal': np.random.choice(['weight-loss', 'maintenance', 'muscle-gain'], n_samples),
            'diet_preference': np.random.choice(['vegan', 'non-vegan'], n_samples)
        }
        
        # Calculate BMI and BMR
        df = pd.DataFrame(data)
        df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
        
        # Calculate BMR using Mifflin-St Jeor Equation
        df['bmr'] = np.where(
            df['gender'] == 'male',
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] + 5,
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] - 161
        )
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'intense': 1.725
        }
        
        df['daily_calories'] = df.apply(
            lambda row: row['bmr'] * activity_multipliers[row['activity_level']], axis=1
        )
        
        # Adjust calories based on goal
        goal_adjustments = {
            'weight-loss': 0.8,
            'maintenance': 1.0,
            'muscle-gain': 1.2
        }
        
        df['target_calories'] = df.apply(
            lambda row: row['daily_calories'] * goal_adjustments[row['goal']], axis=1
        )
        
        logger.info(f"Generated {len(df)} training samples")
        return df
    
    def train_models(self):
        """Train the diet recommendation models"""
        logger.info("Training diet recommendation models...")
        df = self.prepare_sample_data()
        
        # Prepare features for clustering
        categorical_features = ['gender', 'activity_level', 'goal', 'diet_preference']
        numerical_features = ['age', 'weight', 'height', 'bmi', 'bmr']
        
        # Encode categorical variables
        df_encoded = df.copy()
        for feature in categorical_features:
            le = LabelEncoder()
            df_encoded[feature + '_encoded'] = le.fit_transform(df[feature])
            self.label_encoders[feature] = le
        
        # Prepare features for clustering
        cluster_features = numerical_features + [f + '_encoded' for f in categorical_features]
        X_cluster = df_encoded[cluster_features]
        X_cluster_scaled = self.scaler.fit_transform(X_cluster)
        
        # Train K-Means clustering
        logger.info("Training K-Means clustering model...")
        clusters = self.kmeans.fit_predict(X_cluster_scaled)
        df_encoded['cluster'] = clusters
        
        # Train Decision Tree for diet type prediction
        logger.info("Training Decision Tree model...")
        X_tree = df_encoded[cluster_features + ['target_calories']]
        y_tree = df_encoded['diet_preference']
        
        self.decision_tree.fit(X_tree, y_tree)
        
        # Save models
        self.save_models()
        logger.info("Diet recommendation models trained and saved successfully!")
        
        return df_encoded
    
    def predict_diet_plan(self, user_data):
        """Predict personalized diet plan for a user using Gemini 2.5 Flash"""
        try:
            logger.info("Generating diet plan using Gemini 2.5 Flash...")
            
            # Use Gemini service for diet plan generation
            diet_plan = self.gemini_service.generate_diet_plan(user_data)
            
            # Transform the response to match the expected format
            if 'meal_plan' in diet_plan:
                # Convert meal_plan to the format expected by the API
                meal_plan = {}
                for meal_type, meal_data in diet_plan['meal_plan'].items():
                    if isinstance(meal_data, dict):
                        meal_plan[meal_type] = {
                            'name': meal_data.get('name', f'{meal_type.title()}'),
                            'calories': meal_data.get('calories', 0),
                            'protein': meal_data.get('protein', 0),
                            'carbs': meal_data.get('carbs', 0),
                            'fat': meal_data.get('fat', 0)
                        }
                
                return {
                    'target_calories': diet_plan.get('target_calories', 2000),
                    'cluster': 0,  # Not used with Gemini
                    'meal_plan': meal_plan,
                    'macros': diet_plan.get('macros', {
                        'protein': 150,
                        'carbs': 200,
                        'fat': 70
                    }),
                    'recommendations': diet_plan.get('recommendations', '')
                }
            else:
                # Fallback to traditional method if Gemini fails
                logger.warning("Gemini response format unexpected, using fallback")
                return self._fallback_diet_plan(user_data)
                
        except Exception as e:
            logger.error(f"Error predicting diet plan with Gemini: {e}")
            return self._fallback_diet_plan(user_data)
    
    def _fallback_diet_plan(self, user_data):
        """Fallback diet plan using traditional ML approach"""
        try:
            # Calculate BMI and BMR
            bmi = user_data['weight'] / ((user_data['height'] / 100) ** 2)
            
            if user_data['gender'] == 'male':
                bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + 5
            else:
                bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] - 161
            
            # Activity multipliers
            activity_multipliers = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'intense': 1.725
            }
            
            daily_calories = bmr * activity_multipliers[user_data['activity_level']]
            
            # Goal adjustments
            goal_adjustments = {
                'weight-loss': 0.8,
                'maintenance': 1.0,
                'muscle-gain': 1.2
            }
            
            target_calories = daily_calories * goal_adjustments[user_data['goal']]
            
            # Generate meal plan
            meal_plan = self.generate_meal_plan(target_calories, user_data['diet_preference'], user_data['goal'])
            
            return {
                'target_calories': target_calories,
                'cluster': 0,
                'meal_plan': meal_plan,
                'macros': self.calculate_macros(target_calories, user_data['goal'])
            }
        except Exception as e:
            logger.error(f"Error in fallback diet plan: {e}")
            raise
    
    def generate_meal_plan(self, target_calories, diet_preference, goal):
        """Generate personalized meal plan based on calories and preferences"""
        
        # Meal distribution (breakfast: 25%, lunch: 35%, dinner: 40%)
        breakfast_calories = int(target_calories * 0.25)
        lunch_calories = int(target_calories * 0.35)
        dinner_calories = int(target_calories * 0.40)
        
        if diet_preference == 'vegan':
            meals = {
                'breakfast': self.get_vegan_breakfast(breakfast_calories),
                'lunch': self.get_vegan_lunch(lunch_calories),
                'dinner': self.get_vegan_dinner(dinner_calories)
            }
        else:
            meals = {
                'breakfast': self.get_non_vegan_breakfast(breakfast_calories),
                'lunch': self.get_non_vegan_lunch(lunch_calories),
                'dinner': self.get_non_vegan_dinner(dinner_calories)
            }
        
        return meals
    
    def calculate_macros(self, calories, goal):
        """Calculate macro distribution based on goal"""
        if goal == 'weight-loss':
            protein_ratio = 0.30
            carb_ratio = 0.35
            fat_ratio = 0.35
        elif goal == 'muscle-gain':
            protein_ratio = 0.35
            carb_ratio = 0.40
            fat_ratio = 0.25
        else:  # maintenance
            protein_ratio = 0.25
            carb_ratio = 0.45
            fat_ratio = 0.30
        
        return {
            'protein': int((calories * protein_ratio) / 4),  # 4 cal per gram
            'carbs': int((calories * carb_ratio) / 4),      # 4 cal per gram
            'fat': int((calories * fat_ratio) / 9)          # 9 cal per gram
        }
    
    def get_vegan_breakfast(self, calories):
        """Generate vegan breakfast options"""
        options = [
            {'name': 'Oatmeal with berries and nuts', 'calories': calories, 'protein': 12, 'carbs': 54, 'fat': 8},
            {'name': 'Smoothie bowl with fruits', 'calories': calories, 'protein': 10, 'carbs': 48, 'fat': 6},
            {'name': 'Avocado toast with seeds', 'calories': calories, 'protein': 8, 'carbs': 35, 'fat': 15}
        ]
        return np.random.choice(options)
    
    def get_non_vegan_breakfast(self, calories):
        """Generate non-vegan breakfast options"""
        options = [
            {'name': 'Eggs with whole grain toast', 'calories': calories, 'protein': 20, 'carbs': 30, 'fat': 12},
            {'name': 'Greek yogurt with granola', 'calories': calories, 'protein': 18, 'carbs': 35, 'fat': 8},
            {'name': 'Protein pancakes with berries', 'calories': calories, 'protein': 25, 'carbs': 40, 'fat': 6}
        ]
        return np.random.choice(options)
    
    def get_vegan_lunch(self, calories):
        """Generate vegan lunch options"""
        options = [
            {'name': 'Quinoa Buddha bowl', 'calories': calories, 'protein': 15, 'carbs': 65, 'fat': 12},
            {'name': 'Lentil curry with rice', 'calories': calories, 'protein': 18, 'carbs': 70, 'fat': 8},
            {'name': 'Chickpea salad wrap', 'calories': calories, 'protein': 16, 'carbs': 55, 'fat': 14}
        ]
        return np.random.choice(options)
    
    def get_non_vegan_lunch(self, calories):
        """Generate non-vegan lunch options"""
        options = [
            {'name': 'Grilled chicken with quinoa', 'calories': calories, 'protein': 35, 'carbs': 45, 'fat': 10},
            {'name': 'Salmon with sweet potato', 'calories': calories, 'protein': 30, 'carbs': 40, 'fat': 15},
            {'name': 'Turkey and avocado wrap', 'calories': calories, 'protein': 28, 'carbs': 35, 'fat': 18}
        ]
        return np.random.choice(options)
    
    def get_vegan_dinner(self, calories):
        """Generate vegan dinner options"""
        options = [
            {'name': 'Tofu stir-fry with vegetables', 'calories': calories, 'protein': 20, 'carbs': 50, 'fat': 15},
            {'name': 'Black bean and vegetable curry', 'calories': calories, 'protein': 18, 'carbs': 60, 'fat': 12},
            {'name': 'Stuffed bell peppers with quinoa', 'calories': calories, 'protein': 16, 'carbs': 55, 'fat': 10}
        ]
        return np.random.choice(options)
    
    def get_non_vegan_dinner(self, calories):
        """Generate non-vegan dinner options"""
        options = [
            {'name': 'Baked salmon with vegetables', 'calories': calories, 'protein': 40, 'carbs': 30, 'fat': 20},
            {'name': 'Lean beef with brown rice', 'calories': calories, 'protein': 35, 'carbs': 45, 'fat': 15},
            {'name': 'Grilled chicken with sweet potato', 'calories': calories, 'protein': 38, 'carbs': 40, 'fat': 12}
        ]
        return np.random.choice(options)
    
    def save_models(self):
        """Save trained models to disk"""
        models_path = Path(self.config.MODELS_PATH)
        
        joblib.dump(self.kmeans, models_path / 'diet_kmeans_model.pkl')
        joblib.dump(self.decision_tree, models_path / 'diet_decision_tree_model.pkl')
        joblib.dump(self.scaler, models_path / 'diet_scaler.pkl')
        joblib.dump(self.label_encoders, models_path / 'diet_label_encoders.pkl')
        
        logger.info(f"Models saved to {models_path}")
    
    def load_models(self):
        """Load trained models from disk"""
        models_path = Path(self.config.MODELS_PATH)
        
        try:
            self.kmeans = joblib.load(models_path / 'diet_kmeans_model.pkl')
            self.decision_tree = joblib.load(models_path / 'diet_decision_tree_model.pkl')
            self.scaler = joblib.load(models_path / 'diet_scaler.pkl')
            self.label_encoders = joblib.load(models_path / 'diet_label_encoders.pkl')
            logger.info("Diet models loaded successfully")
            return True
        except FileNotFoundError:
            logger.warning("Diet models not found, need to train first")
            return False


class WorkoutRecommendationSystem:
    """
    Gemini 2.5 Flash powered workout recommendation system
    Replaces rule-based system with AI-powered recommendations
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.gemini_service = GeminiRecommendationService(config)
        
        # Keep fallback systems for when Gemini is not available
        self.exercise_database = self.create_exercise_database()
        self.workout_templates = self.create_workout_templates()
    
    def create_exercise_database(self):
        """Create comprehensive exercise database"""
        return {
            'strength': {
                'beginner': [
                    {'name': 'Push-ups', 'muscle_groups': ['chest', 'triceps'], 'equipment': 'bodyweight', 'calories_per_min': 8},
                    {'name': 'Squats', 'muscle_groups': ['legs', 'glutes'], 'equipment': 'bodyweight', 'calories_per_min': 10},
                    {'name': 'Plank', 'muscle_groups': ['core'], 'equipment': 'bodyweight', 'calories_per_min': 5},
                    {'name': 'Lunges', 'muscle_groups': ['legs', 'glutes'], 'equipment': 'bodyweight', 'calories_per_min': 9}
                ],
                'intermediate': [
                    {'name': 'Burpees', 'muscle_groups': ['full_body'], 'equipment': 'bodyweight', 'calories_per_min': 12},
                    {'name': 'Mountain Climbers', 'muscle_groups': ['core', 'cardio'], 'equipment': 'bodyweight', 'calories_per_min': 11},
                    {'name': 'Jump Squats', 'muscle_groups': ['legs', 'cardio'], 'equipment': 'bodyweight', 'calories_per_min': 13},
                    {'name': 'Pike Push-ups', 'muscle_groups': ['shoulders', 'triceps'], 'equipment': 'bodyweight', 'calories_per_min': 9}
                ],
                'advanced': [
                    {'name': 'Pistol Squats', 'muscle_groups': ['legs', 'core'], 'equipment': 'bodyweight', 'calories_per_min': 15},
                    {'name': 'Handstand Push-ups', 'muscle_groups': ['shoulders', 'triceps'], 'equipment': 'bodyweight', 'calories_per_min': 14},
                    {'name': 'Muscle-ups', 'muscle_groups': ['back', 'arms'], 'equipment': 'pull_up_bar', 'calories_per_min': 16}
                ]
            },
            'cardio': {
                'low_intensity': [
                    {'name': 'Walking', 'calories_per_min': 4},
                    {'name': 'Light Jogging', 'calories_per_min': 8},
                    {'name': 'Cycling (leisurely)', 'calories_per_min': 6}
                ],
                'high_intensity': [
                    {'name': 'Running', 'calories_per_min': 12},
                    {'name': 'HIIT Circuit', 'calories_per_min': 15},
                    {'name': 'Jump Rope', 'calories_per_min': 13}
                ]
            }
        }
    
    def create_workout_templates(self):
        """Create workout templates based on time and goals"""
        return {
            '15-30': {
                'weight-loss': ['cardio_hiit', 'bodyweight_circuit'],
                'muscle-gain': ['strength_focused', 'compound_movements'],
                'maintenance': ['balanced_mix']
            },
            '30-45': {
                'weight-loss': ['cardio_strength_combo', 'circuit_training'],
                'muscle-gain': ['strength_training', 'progressive_overload'],
                'maintenance': ['full_body_workout']
            },
            '45-60': {
                'weight-loss': ['extended_cardio', 'strength_cardio_split'],
                'muscle-gain': ['detailed_strength', 'muscle_group_focus'],
                'maintenance': ['comprehensive_workout']
            },
            '60+': {
                'weight-loss': ['long_cardio_sessions', 'detailed_circuits'],
                'muscle-gain': ['advanced_strength', 'split_routines'],
                'maintenance': ['varied_training']
            }
        }
    
    def generate_workout_plan(self, user_data):
        """Generate personalized workout plan using Gemini 2.5 Flash"""
        try:
            logger.info("Generating workout plan using Gemini 2.5 Flash...")
            
            # Use Gemini service for workout plan generation
            workout_plan = self.gemini_service.generate_workout_plan(user_data)
            
            # Transform the response to match the expected format
            if 'exercises' in workout_plan:
                return {
                    'name': workout_plan.get('name', 'AI-Generated Workout'),
                    'duration': workout_plan.get('duration', 30),
                    'difficulty': workout_plan.get('difficulty', 'beginner'),
                    'exercises': workout_plan.get('exercises', []),
                    'estimated_calories': workout_plan.get('estimated_calories', 200),
                    'description': workout_plan.get('description', ''),
                    'equipment_needed': workout_plan.get('equipment_needed', []),
                    'tips': workout_plan.get('tips', '')
                }
            else:
                # Fallback to traditional method if Gemini fails
                logger.warning("Gemini response format unexpected, using fallback")
                return self._fallback_workout_plan(user_data)
                
        except Exception as e:
            logger.error(f"Error generating workout plan with Gemini: {e}")
            return self._fallback_workout_plan(user_data)
    
    def _fallback_workout_plan(self, user_data):
        """Fallback workout plan using traditional rule-based approach"""
        try:
            fitness_level = self.determine_fitness_level(user_data)
            workout_type = self.select_workout_type(user_data['goal'], user_data['workout_time'])
            
            exercises = self.select_exercises(
                workout_type, 
                fitness_level, 
                user_data['workout_time'],
                user_data['goal']
            )
            
            workout_plan = {
                'name': f"{workout_type.replace('_', ' ').title()} Training",
                'duration': self.parse_time_range(user_data['workout_time']),
                'difficulty': fitness_level,
                'exercises': exercises,
                'estimated_calories': sum([ex['calories'] for ex in exercises])
            }
            
            logger.info(f"Generated fallback workout plan: {workout_plan['name']}")
            return workout_plan
        except Exception as e:
            logger.error(f"Error in fallback workout plan: {e}")
            raise
    
    def determine_fitness_level(self, user_data):
        """Determine user's fitness level based on activity level"""
        activity_mapping = {
            'sedentary': 'beginner',
            'light': 'beginner',
            'moderate': 'intermediate',
            'intense': 'advanced'
        }
        return activity_mapping.get(user_data['activity_level'], 'beginner')
    
    def select_workout_type(self, goal, time_available):
        """Select appropriate workout type"""
        templates = self.workout_templates.get(time_available, self.workout_templates['30-45'])
        goal_workouts = templates.get(goal, templates['maintenance'])
        return np.random.choice(goal_workouts)
    
    def select_exercises(self, workout_type, fitness_level, time_available, goal):
        """Select specific exercises for the workout"""
        time_minutes = self.parse_time_range(time_available)
        
        if 'cardio' in workout_type:
            cardio_exercises = self.exercise_database['cardio']['high_intensity']
            strength_exercises = self.exercise_database['strength'][fitness_level]
            exercises = self.mix_cardio_strength(cardio_exercises, strength_exercises, time_minutes, goal)
        else:
            strength_exercises = self.exercise_database['strength'][fitness_level]
            exercises = self.create_strength_workout(strength_exercises, time_minutes, goal)
        
        return exercises
    
    def mix_cardio_strength(self, cardio_exercises, strength_exercises, time_minutes, goal):
        """Mix cardio and strength exercises"""
        exercises = []
        
        # Allocate time: 60% strength, 40% cardio for muscle gain; reverse for weight loss
        if goal == 'muscle-gain':
            strength_time = int(time_minutes * 0.6)
            cardio_time = time_minutes - strength_time
        else:
            cardio_time = int(time_minutes * 0.6)
            strength_time = time_minutes - cardio_time
        
        # Add strength exercises
        selected_strength = np.random.choice(strength_exercises, size=min(4, len(strength_exercises)), replace=False)
        for exercise in selected_strength:
            duration = strength_time // len(selected_strength)
            exercises.append({
                'name': exercise['name'],
                'sets': 3,
                'reps': self.calculate_reps(exercise, goal),
                'duration': duration,
                'calories': exercise['calories_per_min'] * duration,
                'muscle_groups': exercise['muscle_groups'],
                'instructions': self.get_exercise_instructions(exercise['name'])
            })
        
        # Add cardio exercises
        selected_cardio = np.random.choice(cardio_exercises, size=min(2, len(cardio_exercises)), replace=False)
        for exercise in selected_cardio:
            duration = cardio_time // len(selected_cardio)
            exercises.append({
                'name': exercise['name'],
                'sets': 1,
                'reps': f"{duration} minutes",
                'duration': duration,
                'calories': exercise['calories_per_min'] * duration,
                'muscle_groups': ['cardio'],
                'instructions': self.get_exercise_instructions(exercise['name'])
            })
        
        return exercises
    
    def create_strength_workout(self, strength_exercises, time_minutes, goal):
        """Create strength-focused workout"""
        exercises = []
        selected_exercises = np.random.choice(
            strength_exercises, 
            size=min(6, len(strength_exercises)), 
            replace=False
        )
        
        duration_per_exercise = time_minutes // len(selected_exercises)
        
        for exercise in selected_exercises:
            exercises.append({
                'name': exercise['name'],
                'sets': 3 if goal == 'muscle-gain' else 2,
                'reps': self.calculate_reps(exercise, goal),
                'duration': duration_per_exercise,
                'calories': exercise['calories_per_min'] * duration_per_exercise,
                'muscle_groups': exercise['muscle_groups'],
                'instructions': self.get_exercise_instructions(exercise['name'])
            })
        
        return exercises
    
    def calculate_reps(self, exercise, goal):
        """Calculate appropriate reps based on goal"""
        base_reps = {
            'Push-ups': 12,
            'Squats': 15,
            'Lunges': 10,
            'Plank': '30 sec',
            'Burpees': 8,
            'Mountain Climbers': 20
        }
        
        reps = base_reps.get(exercise['name'], 12)
        
        if goal == 'muscle-gain' and isinstance(reps, int):
            return reps + 3
        elif goal == 'weight-loss' and isinstance(reps, int):
            return reps + 5
        
        return reps
    
    def get_exercise_instructions(self, exercise_name):
        """Get detailed instructions for exercises"""
        instructions = {
            'Push-ups': 'Keep your body straight, lower chest to ground, push back up',
            'Squats': 'Feet shoulder-width apart, lower hips back and down, return to standing',
            'Plank': 'Hold body straight from head to heels, engage core muscles',
            'Lunges': 'Step forward, lower hips until both knees at 90 degrees, return to start',
            'Mountain Climbers': 'Start in plank, alternate bringing knees to chest rapidly',
            'Burpees': 'Squat down, jump back to plank, do push-up, jump feet forward, jump up',
            'Running': 'Maintain steady pace, land on midfoot, keep posture upright',
            'Jump Rope': 'Keep elbows close to body, rotate wrists, land softly on balls of feet'
        }
        return instructions.get(exercise_name, 'Follow proper form and breathing technique')
    
    def parse_time_range(self, time_range):
        """Parse time range string to get average minutes"""
        time_mapping = {
            '15-30': 22,
            '30-45': 37,
            '45-60': 52,
            '60+': 75
        }
        return time_mapping.get(time_range, 30)


class CalorieBurnPredictor:
    """
    Gemini 2.5 Flash powered calorie burn prediction system
    Replaces Random Forest with AI-powered predictions
    """
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.gemini_service = GeminiRecommendationService(config)
        
        # Keep fallback models for when Gemini is not available
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
        # Ensure models directory exists
        os.makedirs(self.config.MODELS_PATH, exist_ok=True)
        
    def prepare_training_data(self):
        """Generate training data for calorie burn prediction"""
        logger.info("Generating calorie burn training data...")
        np.random.seed(42)
        n_samples = 2000
        
        # Generate synthetic data
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'weight': np.random.normal(70, 15, n_samples),
            'gender': np.random.choice(['male', 'female'], n_samples),
            'workout_type': np.random.choice(['strength', 'cardio', 'mixed'], n_samples),
            'intensity': np.random.choice(['low', 'moderate', 'high'], n_samples),
            'duration': np.random.randint(15, 90, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Calculate calories burned using MET values
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
        
        df['met'] = df.apply(lambda row: met_values[(row['workout_type'], row['intensity'])], axis=1)
        
        # Calories = MET × weight(kg) × duration(hours)
        df['calories_burned'] = df['met'] * df['weight'] * (df['duration'] / 60)
        
        # Add some noise and gender adjustment
        gender_multiplier = np.where(df['gender'] == 'male', 1.1, 0.9)
        age_factor = 1 - (df['age'] - 25) * 0.002  # Slight decrease with age
        
        df['calories_burned'] = df['calories_burned'] * gender_multiplier * age_factor
        df['calories_burned'] += np.random.normal(0, 10, n_samples)  # Add noise
        df['calories_burned'] = np.maximum(df['calories_burned'], 10)  # Minimum 10 calories
        
        logger.info(f"Generated {len(df)} calorie burn training samples")
        return df
    
    def train_model(self):
        """Train the calorie burn prediction model"""
        logger.info("Training calorie burn prediction model...")
        df = self.prepare_training_data()
        
        # Encode categorical variables
        categorical_features = ['gender', 'workout_type', 'intensity']
        for feature in categorical_features:
            le = LabelEncoder()
            df[feature + '_encoded'] = le.fit_transform(df[feature])
            self.label_encoders[feature] = le
        
        # Prepare features
        feature_columns = ['age', 'weight', 'duration'] + [f + '_encoded' for f in categorical_features]
        X = df[feature_columns]
        y = df['calories_burned']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        logger.info("Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f"Training R² Score: {train_score:.3f}")
        logger.info(f"Testing R² Score: {test_score:.3f}")
        
        # Save model
        self.save_model()
        logger.info("Calorie burn prediction model trained and saved successfully!")
        
        return test_score
    
    def predict_calories(self, user_data, workout_data):
        """Predict calories burned for a specific workout using Gemini 2.5 Flash"""
        try:
            logger.info("Predicting calories using Gemini 2.5 Flash...")
            
            # Use Gemini service for calorie prediction
            calories = self.gemini_service.predict_calories_burned(user_data, workout_data)
            
            return max(int(calories), 10)  # Minimum 10 calories
            
        except Exception as e:
            logger.error(f"Error predicting calories with Gemini: {e}")
            return self._fallback_calorie_prediction(user_data, workout_data)
    
    def _fallback_calorie_prediction(self, user_data, workout_data):
        """Fallback calorie prediction using traditional ML approach"""
        try:
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
        except Exception as e:
            logger.error(f"Error in fallback calorie prediction: {e}")
            return 100  # Default fallback
    
    def save_model(self):
        """Save the trained model"""
        models_path = Path(self.config.MODELS_PATH)
        
        joblib.dump(self.model, models_path / 'calorie_burn_model.pkl')
        joblib.dump(self.scaler, models_path / 'calorie_burn_scaler.pkl')
        joblib.dump(self.label_encoders, models_path / 'calorie_burn_encoders.pkl')
        
        logger.info(f"Calorie models saved to {models_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        models_path = Path(self.config.MODELS_PATH)
        
        try:
            self.model = joblib.load(models_path / 'calorie_burn_model.pkl')
            self.scaler = joblib.load(models_path / 'calorie_burn_scaler.pkl')
            self.label_encoders = joblib.load(models_path / 'calorie_burn_encoders.pkl')
            logger.info("Calorie models loaded successfully")
            return True
        except FileNotFoundError:
            logger.warning("Calorie models not found, need to train first")
            return False


def main():
    """Main function to train all models"""
    print("=== AI-Powered Diet and Workout Recommendation System ===")
    print("VS Code Optimized Version")
    print("Training Machine Learning Models...\n")
    
    # Get configuration
    config = get_config()
    
    # Train Diet Recommendation System
    print("1. Training Diet Recommendation System...")
    diet_system = DietRecommendationSystem(config)
    diet_data = diet_system.train_models()
    print("✓ Diet recommendation models trained successfully!\n")
    
    # Train Calorie Burn Predictor
    print("2. Training Calorie Burn Predictor...")
    calorie_predictor = CalorieBurnPredictor(config)
    calorie_score = calorie_predictor.train_model()
    print("✓ Calorie burn prediction model trained successfully!\n")
    
    # Test the systems with sample user
    print("3. Testing systems with sample user...")
    sample_user = {
        'age': 28,
        'weight': 70,
        'height': 175,
        'gender': 'male',
        'activity_level': 'moderate',
        'goal': 'weight-loss',
        'diet_preference': 'non-vegan',
        'workout_time': '30-45'
    }
    
    # Test diet recommendation
    diet_plan = diet_system.predict_diet_plan(sample_user)
    print(f"Sample Diet Plan - Target Calories: {diet_plan['target_calories']:.0f}")
    print(f"Macros - Protein: {diet_plan['macros']['protein']}g, Carbs: {diet_plan['macros']['carbs']}g, Fat: {diet_plan['macros']['fat']}g")
    
    # Test workout recommendation
    workout_system = WorkoutRecommendationSystem(config)
    workout_plan = workout_system.generate_workout_plan(sample_user)
    print(f"Sample Workout: {workout_plan['name']} - {workout_plan['duration']} minutes")
    print(f"Estimated Calories: {workout_plan['estimated_calories']}")
    
    # Test calorie prediction
    workout_data = {
        'type': 'mixed',
        'intensity': 'moderate',
        'duration': 37
    }
    predicted_calories = calorie_predictor.predict_calories(sample_user, workout_data)
    print(f"Predicted Calorie Burn: {predicted_calories} calories")
    
    print("\n✓ All models trained and tested successfully!")
    print("Models saved to disk and ready for integration with the web application.")
    print(f"Models location: {config.MODELS_PATH}")

if __name__ == "__main__":
    main()
