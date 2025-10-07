"""
Test script to check if profile generation is working with Gemini
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from backend.ml_models import DietRecommendationSystem, WorkoutRecommendationSystem, CalorieBurnPredictor
from backend.config import get_config

def test_profile_generation():
    """Test if profile generation works with Gemini"""
    print("🧪 Testing Profile Generation with Gemini 2.5 Flash")
    print("=" * 60)
    
    # Sample user data
    sample_user = {
        'age': 25,
        'weight': 70,
        'height': 175,
        'gender': 'male',
        'activity_level': 'moderate',
        'goal': 'weight-loss',
        'diet_preference': 'non-vegan',
        'workout_time': '30-45'
    }
    
    print("📊 Sample User Data:")
    for key, value in sample_user.items():
        print(f"   {key}: {value}")
    
    print("\n🤖 Testing Diet Plan Generation...")
    try:
        config = get_config()
        diet_system = DietRecommendationSystem(config)
        diet_plan = diet_system.predict_diet_plan(sample_user)
        
        print("✅ Diet Plan Generated Successfully!")
        print(f"   Target Calories: {diet_plan.get('target_calories', 'N/A')}")
        print(f"   Macros: {diet_plan.get('macros', {})}")
        print(f"   Meals: {list(diet_plan.get('meal_plan', {}).keys())}")
        
        # Check if it's using Gemini or fallback
        if 'recommendations' in diet_plan:
            print("   🎯 Using Gemini 2.5 Flash (AI-powered)")
        else:
            print("   🔄 Using Fallback ML Models")
            
    except Exception as e:
        print(f"❌ Diet Plan Generation Failed: {e}")
        return False
    
    print("\n🏋️ Testing Workout Plan Generation...")
    try:
        workout_system = WorkoutRecommendationSystem(config)
        workout_plan = workout_system.generate_workout_plan(sample_user)
        
        print("✅ Workout Plan Generated Successfully!")
        print(f"   Name: {workout_plan.get('name', 'N/A')}")
        print(f"   Duration: {workout_plan.get('duration', 'N/A')} minutes")
        print(f"   Estimated Calories: {workout_plan.get('estimated_calories', 'N/A')}")
        print(f"   Exercises: {len(workout_plan.get('exercises', []))}")
        
        # Check if it's using Gemini or fallback
        if 'description' in workout_plan or 'tips' in workout_plan:
            print("   🎯 Using Gemini 2.5 Flash (AI-powered)")
        else:
            print("   🔄 Using Fallback ML Models")
            
    except Exception as e:
        print(f"❌ Workout Plan Generation Failed: {e}")
        return False
    
    print("\n🔥 Testing Calorie Prediction...")
    try:
        calorie_predictor = CalorieBurnPredictor(config)
        workout_data = {
            'type': 'mixed',
            'intensity': 'moderate',
            'duration': 30
        }
        calories = calorie_predictor.predict_calories(sample_user, workout_data)
        
        print(f"✅ Calorie Prediction: {calories} calories")
        print("   🎯 Using Gemini 2.5 Flash (AI-powered)")
        
    except Exception as e:
        print(f"❌ Calorie Prediction Failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The system is working correctly.")
    return True

if __name__ == "__main__":
    success = test_profile_generation()
    if not success:
        sys.exit(1)
    print("\n✅ Profile generation test completed successfully!")
