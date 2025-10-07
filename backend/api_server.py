"""
Flask API Server for AI Diet and Workout Recommendation System
VS Code optimized version with proper error handling, logging, and configuration
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import psycopg2
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from backend.ml_models import DietRecommendationSystem, WorkoutRecommendationSystem, CalorieBurnPredictor
from backend.database_setup import DatabaseManager
from backend.config import get_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    
    app.config.from_object(config)
    config.init_app(app)
    
    # Session configuration for cross-origin requests
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Setup CORS
    CORS(app, supports_credentials=True, origins=config.CORS_ORIGINS)
    
    # Initialize systems
    db = DatabaseManager(config.DATABASE_URL)
    diet_system = DietRecommendationSystem(config)
    workout_system = WorkoutRecommendationSystem(config)
    calorie_predictor = CalorieBurnPredictor(config)
    
    # Try to load trained models
    try:
        diet_system.load_models()
        calorie_predictor.load_model()
        logger.info("✅ ML models loaded successfully!")
    except Exception as e:
        logger.warning(f"⚠️ ML models not found: {e}")
        logger.info("Please run 'python backend/ml_models.py' first to train the models.")
    
    # Routes
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'success': True,
            'message': 'AI Diet & Workout API is running',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    @app.route('/api/register', methods=['POST'])
    def register():
        """Register a new user"""
        try:
            data = request.get_json()
            
            if not data or not all(k in data for k in ['email', 'password', 'name']):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: email, password, name'
                }), 400
            
            user_id = db.create_user(
                email=data['email'],
                password=data['password'],
                name=data['name']
            )
            
            if user_id:
                session['user_id'] = user_id
                logger.info(f"New user registered: {data['email']}")
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
            logger.error(f"Registration error: {e}")
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            }), 500

    @app.route('/api/login', methods=['POST'])
    def login():
        """Authenticate user login"""
        try:
            data = request.get_json()
            
            if not data or not all(k in data for k in ['email', 'password']):
                return jsonify({
                    'success': False,
                    'message': 'Missing email or password'
                }), 400
            
            user = db.authenticate_user(data['email'], data['password'])
            
            if user:
                session['user_id'] = user['id']
                
                # Check if user has completed profile
                profile = db.get_user_profile(user['id'])
                
                logger.info(f"User logged in: {data['email']}")
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
            logger.error(f"Login error: {e}")
            return jsonify({
                'success': False,
                'message': f'Login failed: {str(e)}'
            }), 500

    @app.route('/api/logout', methods=['POST'])
    def logout():
        """Logout user"""
        session.pop('user_id', None)
        return jsonify({'success': True, 'message': 'Logged out successfully'})

    @app.route('/api/profile', methods=['GET'])
    def get_profile():
        """Get current user profile"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            
            # Get user info
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            cursor.execute('SELECT id, email, name FROM users WHERE id = %s', (user_id,))
            user_result = cursor.fetchone()
            
            if not user_result:
                conn.close()
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            user_id, email, name = user_result
            
            # Get profile info
            profile = db.get_user_profile(user_id)
            profile_complete = profile is not None
            
            conn.close()
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'profile_complete': profile_complete
                },
                'profile': profile
            })
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get profile: {str(e)}'
            }), 500

    @app.route('/api/profile', methods=['POST'])
    def save_profile():
        """Save user profile and generate recommendations"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            data = request.get_json()
            user_id = session['user_id']
            
            logger.info(f"Received profile data: {data}")
            
            if not data:
                return jsonify({
                    'success': False,
                    'message': 'No profile data provided'
                }), 400
            
            # Validate required fields
            required_fields = ['age', 'gender', 'height', 'weight', 'goal', 
                             'diet_preference', 'activity_level', 'workout_time']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                logger.warning(f"Missing fields: {missing_fields}")
                return jsonify({
                    'success': False,
                    'message': f'Missing required fields: {missing_fields}'
                }), 400
            
            # Generate diet plan first to get target calories
            diet_plan = diet_system.predict_diet_plan(data)
            
            # Add target calories to profile data
            data['target_calories'] = diet_plan.get('target_calories', 2000)
            
            # Save profile to database with target calories
            db.save_user_profile(user_id, data)
            
            # Generate workout plan
            workout_plan = workout_system.generate_workout_plan(data)
            
            # Save plans to database
            today = datetime.now().strftime('%Y-%m-%d')
            db.save_diet_plan(user_id, today, diet_plan['meal_plan'])
            db.save_workout_plan(user_id, today, workout_plan)
            
            logger.info(f"Profile saved and plans generated for user {user_id}")
            return jsonify({
                'success': True,
                'message': 'Profile saved and plans generated',
                'diet_plan': diet_plan,
                'workout_plan': workout_plan
            })
            
        except Exception as e:
            logger.error(f"Profile save error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to save profile: {str(e)}'
            }), 500

    @app.route('/api/diet-plan', methods=['GET'])
    def get_diet_plan():
        """Get current diet plan"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT meal_type, food_item, calories, protein, carbs, fat
                FROM diet_plans 
                WHERE user_id = %s AND date = %s
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
            logger.error(f"Diet plan retrieval error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get diet plan: {str(e)}'
            }), 500

    @app.route('/api/workout-plan', methods=['GET'])
    def get_workout_plan():
        """Get current workout plan"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT workout_name, exercise_name, sets, reps, duration, calories_burned, completed
                FROM workout_plans 
                WHERE user_id = %s AND date = %s
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
            logger.error(f"Workout plan retrieval error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get workout plan: {str(e)}'
            }), 500

    @app.route('/api/workout-plan', methods=['POST'])
    def generate_custom_workout():
        """Generate custom workout plan based on user preferences"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            data = request.get_json()
            
            # Get customization parameters
            duration = data.get('duration', 30)
            difficulty = data.get('difficulty', 'intermediate')
            focus_areas = data.get('focus_areas', [])
            equipment = data.get('equipment', [])
            workout_type = data.get('workout_type', 'full_body')
            
            # Get user profile for context
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT age, height, weight, activity_level, goal
                FROM user_profiles 
                WHERE user_id = %s
            ''', (user_id,))
            profile = cursor.fetchone()
            conn.close()
            
            if not profile:
                return jsonify({'success': False, 'message': 'User profile not found'}), 404
            
            age, height, weight, activity_level, goals = profile
            
            # Generate custom workout using Gemini
            from gemini_service import GeminiRecommendationService
            gemini_service = GeminiRecommendationService()
            
            workout_prompt = f"""
            Generate a custom workout plan with the following specifications:
            
            User Profile:
            - Age: {age}
            - Height: {height} cm
            - Weight: {weight} kg
            - Activity Level: {activity_level}
            - Goals: {goals}
            
            Workout Customization:
            - Duration: {duration} minutes
            - Difficulty: {difficulty}
            - Focus Areas: {', '.join(focus_areas) if focus_areas else 'General fitness'}
            - Available Equipment: {', '.join(equipment) if equipment else 'No equipment'}
            - Workout Type: {workout_type}
            
            Please generate a detailed workout plan with:
            1. Workout name
            2. List of exercises with:
               - Exercise name
               - Sets and reps
               - Duration per exercise
               - Estimated calories burned
               - Instructions
               - Muscle groups targeted
            
            IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. The response must start with {{ and end with }}.
            
            Format the response as JSON with the structure:
            {{
                "workout_name": "Custom Workout Name",
                "exercises": [
                    {{
                        "name": "Exercise Name",
                        "sets": 3,
                        "reps": "10-12",
                        "duration": 5,
                        "calories": 50,
                        "instructions": "Detailed instructions",
                        "muscle_groups": ["Muscle Group 1", "Muscle Group 2"]
                    }}
                ],
                "total_duration": {duration},
                "total_calories": 300
            }}
            """
            
            workout_response = gemini_service.generate_workout_plan_from_prompt(workout_prompt)
            
            # Parse the response and save to database
            import json
            try:
                logger.info(f"Attempting to parse workout response: {workout_response[:200]}...")
                workout_data = json.loads(workout_response)
                
                # Validate the workout data structure
                if 'workout_name' not in workout_data or 'exercises' not in workout_data:
                    logger.error(f"Invalid workout data structure: {workout_data}")
                    return jsonify({
                        'success': False,
                        'message': 'Invalid workout plan format received. Please try again.'
                    }), 500
                
                logger.info(f"Successfully parsed workout data with {len(workout_data.get('exercises', []))} exercises")
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Raw response: {workout_response}")
                return jsonify({
                    'success': False,
                    'message': 'Failed to parse workout plan response. Please try again.'
                }), 500
            
            # Save workout plan to database
            try:
                conn = psycopg2.connect(db.db_url)
                cursor = conn.cursor()
                
                # Clear existing workout for today
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('DELETE FROM workout_plans WHERE user_id = %s AND date = %s', (user_id, today))
                
                # Insert new workout plan
                for exercise in workout_data['exercises']:
                    cursor.execute('''
                        INSERT INTO workout_plans 
                        (user_id, date, workout_name, exercise_name, sets, reps, duration, calories_burned, completed)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        user_id, today, workout_data['workout_name'],
                        exercise.get('name', 'Unknown Exercise'), 
                        exercise.get('sets', 1), 
                        str(exercise.get('reps', '10')),
                        exercise.get('duration', 5), 
                        exercise.get('calories', 50), 
                        False
                    ))
                
                conn.commit()
                conn.close()
                
            except Exception as db_error:
                logger.error(f"Database error while saving workout: {db_error}")
                return jsonify({
                    'success': False,
                    'message': 'Failed to save workout plan to database. Please try again.'
                }), 500
            
            return jsonify({
                'success': True,
                'workout': workout_data
            })
            
        except Exception as e:
            logger.error(f"Custom workout generation error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to generate custom workout: {str(e)}'
            }), 500

    @app.route('/api/log-progress', methods=['POST'])
    def log_progress():
        """Log daily progress"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            data = request.get_json()
            user_id = session['user_id']
            
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
            logger.error(f"Progress logging error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to log progress: {str(e)}'
            }), 500

    @app.route('/api/progress-data', methods=['GET'])
    def get_progress_data():
        """Get user progress data"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            days = int(request.args.get('days', 30))
            
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
            logger.error(f"Progress data retrieval error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get progress data: {str(e)}'
            }), 500

    @app.route('/api/predict-calories', methods=['POST'])
    def predict_calories():
        """Predict calories burned for a workout"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            data = request.get_json()
            user_id = session['user_id']
            
            if not data or not all(k in data for k in ['workout_type', 'intensity', 'duration']):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: workout_type, intensity, duration'
                }), 400
            
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
            logger.error(f"Calorie prediction error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to predict calories: {str(e)}'
            }), 500

    @app.route('/api/dashboard-stats', methods=['GET'])
    def get_dashboard_stats():
        """Get dashboard statistics"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            user_id = session['user_id']
            # Get today's data
            today = datetime.now().strftime('%Y-%m-%d')
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            
            # Get today's diet plan calories (sum of all meals)
            cursor.execute('''
                SELECT SUM(calories) FROM diet_plans 
                WHERE user_id = %s AND date = %s
            ''', (user_id, today))
            result = cursor.fetchone()
            calories_planned = result[0] if result and result[0] else 0
            
            # Get today's workout calories (sum of all exercises)
            cursor.execute('''
                SELECT SUM(calories_burned) FROM workout_plans 
                WHERE user_id = %s AND date = %s
            ''', (user_id, today))
            result = cursor.fetchone()
            calories_workout = result[0] if result and result[0] else 0
            
            # Get completed workouts count
            cursor.execute('''
                SELECT COUNT(*) FROM workout_plans 
                WHERE user_id = %s AND date = %s AND completed = true
            ''', (user_id, today))
            result = cursor.fetchone()
            workouts_completed = result[0] if result and result[0] else 0
            
            # Get total planned workouts count
            cursor.execute('''
                SELECT COUNT(*) FROM workout_plans 
                WHERE user_id = %s AND date = %s
            ''', (user_id, today))
            result = cursor.fetchone()
            workouts_planned = result[0] if result and result[0] else 0
            
            # Get today's progress log (if any)
            cursor.execute('''
                SELECT calories_consumed, calories_burned, workouts_completed 
                FROM daily_logs 
                WHERE user_id = %s AND date = %s
            ''', (user_id, today))
            log_data = cursor.fetchone()
            
            # Get user profile for target calories
            profile = db.get_user_profile(user_id)
            target_calories = profile['target_calories'] if profile else 2000
            
            conn.close()
            
            # Calculate stats - prioritize logged data, fallback to planned data
            calories_consumed = log_data[0] if log_data and log_data[0] else 0
            calories_burned = log_data[1] if log_data and log_data[1] else calories_workout
            workouts_completed_logged = log_data[2] if log_data and log_data[2] else workouts_completed
            
            stats = {
                'calories_target': target_calories,
                'calories_planned': calories_planned,
                'calories_consumed': calories_consumed,
                'calories_burned': calories_burned,
                'workouts_completed': workouts_completed_logged,
                'workouts_planned': workouts_planned
            }
            
            logger.info(f"Dashboard stats for user {user_id}: {stats}")
            return jsonify({
                'success': True,
                'stats': stats
            })
        except Exception as e:
            logger.error(f"Dashboard stats error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to get dashboard stats: {str(e)}'
            }), 500

    @app.route('/api/complete-exercise', methods=['POST'])
    def complete_exercise():
        """Mark an exercise as completed"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        
        try:
            data = request.get_json()
            user_id = session['user_id']
            if not data or not all(k in data for k in ['date', 'exercise_name']):
                return jsonify({
                    'success': False,
                    'message': 'Missing required fields: date, exercise_name'
                }), 400
            conn = psycopg2.connect(db.db_url)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE workout_plans SET completed = TRUE
                WHERE user_id = %s AND date = %s AND exercise_name = %s
            ''', (user_id, data['date'], data['exercise_name']))
            conn.commit()
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Exercise marked as completed'
            })
        except Exception as e:
            logger.error(f"Exercise completion error: {e}")
            return jsonify({
                'success': False,
                'message': f'Failed to complete exercise: {str(e)}'
            }), 500

    return app

def main():
    """Main function to run the Flask server"""
    print("=== AI Diet & Workout API Server ===")
    print("VS Code Optimized Version")
    print("Starting Flask server...")
    
    # Get configuration
    config = get_config()
    
    # Create app
    app = create_app(config)
    
    print(f"API will be available at: http://{config.API_HOST}:{config.API_PORT}")
    print("\nAvailable endpoints:")
    print("- GET  /api/health - Health check")
    print("- POST /api/register - Register new user")
    print("- POST /api/login - User login")
    print("- POST /api/logout - User logout")
    print("- POST /api/profile - Save user profile")
    print("- GET  /api/diet-plan - Get diet plan")
    print("- GET  /api/workout-plan - Get workout plan")
    print("- POST /api/log-progress - Log daily progress")
    print("- GET  /api/progress-data - Get progress data")
    print("- POST /api/predict-calories - Predict calorie burn")
    print("- GET  /api/dashboard-stats - Get dashboard statistics")
    print("- POST /api/complete-exercise - Mark exercise complete")
    
    print("\n🎮 Demo user credentials:")
    print("Email: demo@example.com")
    print("Password: password123")
    
    print("\n🐛 VS Code Integration:")
    print("- Use F5 to start debugging")
    print("- Set breakpoints in the code")
    print("- Use integrated terminal for testing")
    
    # Run the app
    try:
        app.run(
            host=config.API_HOST,
            port=config.API_PORT,
            debug=config.DEBUG
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user. Goodbye!")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"❌ Server failed to start: {e}")

if __name__ == '__main__':
    main()
