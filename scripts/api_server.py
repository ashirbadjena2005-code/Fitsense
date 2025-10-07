"""
Flask API Server for AI Diet and Workout Recommendation System
This script provides REST API endpoints for the frontend application.
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_models import DietRecommendationSystem, WorkoutRecommendationSystem, CalorieBurnPredictor
from database_setup import DatabaseManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
CORS(app, supports_credentials=True)

# Initialize systems
db = DatabaseManager()
diet_system = DietRecommendationSystem()
workout_system = WorkoutRecommendationSystem()
calorie_predictor = CalorieBurnPredictor()

# Load trained models (train them first if they don't exist)
try:
    import joblib
    diet_system.kmeans = joblib.load('diet_kmeans_model.pkl')
    diet_system.decision_tree = joblib.load('diet_decision_tree_model.pkl')
    diet_system.scaler = joblib.load('diet_scaler.pkl')
    diet_system.label_encoders = joblib.load('diet_label_encoders.pkl')
    
    calorie_predictor.model = joblib.load('calorie_burn_model.pkl')
    calorie_predictor.scaler = joblib.load('calorie_burn_scaler.pkl')
    calorie_predictor.label_encoders = joblib.load('calorie_burn_encoders.pkl')
    
    print("✓ ML models loaded successfully!")
except FileNotFoundError:
    print("⚠ ML models not found. Please run ml_models.py first to train the models.")

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    try:
        user_id = db.create_user(
            email=data['email'],
            password=data['password'],
            name=data['name']
        )
        
        if user_id:
            session['user_id'] = user_id
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'user': {
                    'id': user_id,
                    'email': data['email'],
                    'name': data['name']
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user login"""
    data = request.get_json()
    
    try:
        user = db.authenticate_user(data['email'], data['password'])
        
        if user:
            session['user_id'] = user['id']
            
            # Check if user has completed profile
            profile = db.get_user_profile(user['id'])
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'profile_complete': profile is not None
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/profile', methods=['POST'])
def save_profile():
    """Save user profile and generate recommendations"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        # Save profile to database
        db.save_user_profile(user_id, data)
        
        # Generate diet plan
        diet_plan = diet_system.predict_diet_plan(data)
        
        # Generate workout plan
        workout_plan = workout_system.generate_workout_plan(data)
        
        # Save plans to database
        today = datetime.now().strftime('%Y-%m-%d')
        db.save_diet_plan(user_id, today, diet_plan['meal_plan'])
        db.save_workout_plan(user_id, today, workout_plan)
        
        return jsonify({
            'success': True,
            'message': 'Profile saved and plans generated',
            'diet_plan': diet_plan,
            'workout_plan': workout_plan
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to save profile: {str(e)}'
        }), 500

@app.route('/api/diet-plan', methods=['GET'])
def get_diet_plan():
    """Get current diet plan"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT meal_type, food_item, calories, protein, carbs, fat
            FROM diet_plans 
            WHERE user_id = ? AND date = ?
            ORDER BY meal_type, id
        ''', (user_id, date))
        
        results = cursor.fetchall()
        conn.close()
        
        # Organize by meal type
        meals = {}
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for row in results:
            meal_type, food_item, calories, protein, carbs, fat = row
            
            if meal_type not in meals:
                meals[meal_type] = []
            
            meals[meal_type].append({
                'name': food_item,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat
            })
            
            total_calories += calories
            total_protein += protein
            total_carbs += carbs
            total_fat += fat
        
        return jsonify({
            'success': True,
            'meals': meals,
            'totals': {
                'calories': total_calories,
                'protein': total_protein,
                'carbs': total_carbs,
                'fat': total_fat
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get diet plan: {str(e)}'
        }), 500

@app.route('/api/workout-plan', methods=['GET'])
def get_workout_plan():
    """Get current workout plan"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT workout_name, exercise_name, sets, reps, duration, calories_burned, completed
            FROM workout_plans 
            WHERE user_id = ? AND date = ?
            ORDER BY id
        ''', (user_id, date))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return jsonify({'success': False, 'message': 'No workout plan found'})
        
        workout_name = results[0][0]
        exercises = []
        total_duration = 0
        total_calories = 0
        
        for row in results:
            _, exercise_name, sets, reps, duration, calories_burned, completed = row
            
            exercises.append({
                'name': exercise_name,
                'sets': sets,
                'reps': reps,
                'duration': duration,
                'calories': calories_burned,
                'completed': bool(completed)
            })
            
            total_duration += duration or 0
            total_calories += calories_burned or 0
        
        return jsonify({
            'success': True,
            'workout': {
                'name': workout_name,
                'exercises': exercises,
                'total_duration': total_duration,
                'total_calories': total_calories
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get workout plan: {str(e)}'
        }), 500

@app.route('/api/log-progress', methods=['POST'])
def log_progress():
    """Log daily progress"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        db.log_daily_progress(
            user_id=user_id,
            date=data.get('date', datetime.now().strftime('%Y-%m-%d')),
            weight=data.get('weight'),
            calories_consumed=data.get('calories_consumed'),
            calories_burned=data.get('calories_burned'),
            workouts_completed=data.get('workouts_completed'),
            notes=data.get('notes')
        )
        
        return jsonify({
            'success': True,
            'message': 'Progress logged successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to log progress: {str(e)}'
        }), 500

@app.route('/api/progress-data', methods=['GET'])
def get_progress_data():
    """Get user progress data"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    days = int(request.args.get('days', 30))
    
    try:
        df = db.get_progress_data(user_id, days)
        
        # Convert DataFrame to JSON-serializable format
        progress_data = {
            'dates': df['date'].tolist(),
            'weights': df['weight'].fillna(0).tolist(),
            'calories_consumed': df['calories_consumed'].fillna(0).tolist(),
            'calories_burned': df['calories_burned'].fillna(0).tolist(),
            'workouts_completed': df['workouts_completed'].fillna(0).tolist()
        }
        
        return jsonify({
            'success': True,
            'data': progress_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get progress data: {str(e)}'
        }), 500

@app.route('/api/predict-calories', methods=['POST'])
def predict_calories():
    """Predict calories burned for a workout"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        # Get user profile
        profile = db.get_user_profile(user_id)
        if not profile:
            return jsonify({'success': False, 'message': 'User profile not found'}), 404
        
        # Predict calories
        predicted_calories = calorie_predictor.predict_calories(
            user_data={
                'age': profile['age'],
                'weight': profile['weight'],
                'gender': profile['gender']
            },
            workout_data={
                'type': data['workout_type'],
                'intensity': data['intensity'],
                'duration': data['duration']
            }
        )
        
        return jsonify({
            'success': True,
            'predicted_calories': predicted_calories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to predict calories: {str(e)}'
        }), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    try:
        # Get today's data
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get today's diet plan calories
        cursor.execute('''
            SELECT SUM(calories) FROM diet_plans 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        calories_planned = cursor.fetchone()[0] or 0
        
        # Get today's workout calories
        cursor.execute('''
            SELECT SUM(calories_burned) FROM workout_plans 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        calories_workout = cursor.fetchone()[0] or 0
        
        # Get today's progress log
        cursor.execute('''
            SELECT calories_consumed, calories_burned, workouts_completed 
            FROM daily_logs 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        log_data = cursor.fetchone()
        
        # Get user profile for target calories
        profile = db.get_user_profile(user_id)
        target_calories = profile['target_calories'] if profile else 2000
        
        conn.close()
        
        stats = {
            'calories_target': target_calories,
            'calories_planned': calories_planned,
            'calories_consumed': log_data[0] if log_data and log_data[0] else 0,
            'calories_burned': log_data[1] if log_data and log_data[1] else calories_workout,
            'workouts_completed': log_data[2] if log_data and log_data[2] else 0,
            'workouts_planned': 1 if calories_workout > 0 else 0
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get dashboard stats: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/complete-exercise', methods=['POST'])
def complete_exercise():
    """Mark an exercise as completed"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE workout_plans SET completed = TRUE
            WHERE user_id = ? AND date = ? AND exercise_name = ?
        ''', (user_id, data['date'], data['exercise_name']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Exercise marked as completed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to complete exercise: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("=== AI Diet & Workout API Server ===")
    print("Starting Flask server...")
    print("API will be available at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("- POST /api/register - Register new user")
    print("- POST /api/login - User login")
    print("- POST /api/logout - User logout")
    print("- POST /api/profile - Save user profile")
    print("- GET /api/diet-plan - Get diet plan")
    print("- GET /api/workout-plan - Get workout plan")
    print("- POST /api/log-progress - Log daily progress")
    print("- GET /api/progress-data - Get progress data")
    print("- POST /api/predict-calories - Predict calorie burn")
    print("- GET /api/dashboard-stats - Get dashboard statistics")
    print("- GET /api/health - Health check")
    print("\nDemo user credentials:")
    print("Email: demo@example.com")
    print("Password: password123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
