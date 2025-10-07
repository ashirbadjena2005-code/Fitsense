"""
Test script for Gemini 2.5 Flash integration
Run this to verify the integration is working properly
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from backend.gemini_service import GeminiRecommendationService
from backend.config import get_config

def test_gemini_integration():
    """Test the Gemini integration with sample data"""
    print("🤖 Testing Gemini 2.5 Flash Integration")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        print("Or add it to your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize the service
    config = get_config()
    service = GeminiRecommendationService(config)
    
    if not service.model:
        print("❌ Failed to initialize Gemini model")
        return False
    
    print("✅ Gemini service initialized successfully!")
    
    # Test data
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
    
    print("\n🧪 Testing Diet Plan Generation...")
    try:
        diet_plan = service.generate_diet_plan(sample_user)
        print("✅ Diet plan generated successfully!")
        print(f"   Target Calories: {diet_plan.get('target_calories', 'N/A')}")
        print(f"   Macros: {diet_plan.get('macros', {})}")
        print(f"   Meals: {list(diet_plan.get('meal_plan', {}).keys())}")
    except Exception as e:
        print(f"❌ Diet plan generation failed: {e}")
        return False
    
    print("\n🏋️ Testing Workout Plan Generation...")
    try:
        workout_plan = service.generate_workout_plan(sample_user)
        print("✅ Workout plan generated successfully!")
        print(f"   Name: {workout_plan.get('name', 'N/A')}")
        print(f"   Duration: {workout_plan.get('duration', 'N/A')} minutes")
        print(f"   Exercises: {len(workout_plan.get('exercises', []))}")
    except Exception as e:
        print(f"❌ Workout plan generation failed: {e}")
        return False
    
    print("\n🔥 Testing Calorie Prediction...")
    try:
        workout_data = {
            'type': 'mixed',
            'intensity': 'moderate',
            'duration': 30
        }
        calories = service.predict_calories_burned(sample_user, workout_data)
        print(f"✅ Calorie prediction successful: {calories} calories")
    except Exception as e:
        print(f"❌ Calorie prediction failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Gemini integration is working correctly.")
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    if not success:
        sys.exit(1)
    print("\n✅ Integration test completed successfully!")
