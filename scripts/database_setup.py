"""
Database setup and management for the AI Diet and Workout System
This script creates and manages the SQLite database for user data, meal plans, and workout logs.
"""

import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
import pandas as pd

class DatabaseManager:
    """
    Manages all database operations for the fitness application
    """
    
    def __init__(self, db_path='fitness_app.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                height REAL NOT NULL,
                weight REAL NOT NULL,
                goal TEXT NOT NULL,
                diet_preference TEXT NOT NULL,
                activity_level TEXT NOT NULL,
                workout_time TEXT NOT NULL,
                target_calories REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Diet plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                food_item TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Workout plans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                workout_name TEXT NOT NULL,
                exercise_name TEXT NOT NULL,
                sets INTEGER,
                reps TEXT,
                duration INTEGER,
                calories_burned REAL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Daily logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                weight REAL,
                calories_consumed REAL,
                calories_burned REAL,
                workouts_completed INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Food database table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_database (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                calories_per_100g REAL NOT NULL,
                protein_per_100g REAL NOT NULL,
                carbs_per_100g REAL NOT NULL,
                fat_per_100g REAL NOT NULL,
                is_vegan BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Exercise database table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_database (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                muscle_groups TEXT NOT NULL,
                equipment TEXT,
                difficulty_level TEXT NOT NULL,
                calories_per_minute REAL NOT NULL,
                instructions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email, password, name):
        """Create a new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # User already exists
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT id, name FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {'id': result[0], 'name': result[1], 'email': email}
        return None
    
    def save_user_profile(self, user_id, profile_data):
        """Save or update user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if profile exists
        cursor.execute('SELECT id FROM user_profiles WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing profile
            cursor.execute('''
                UPDATE user_profiles SET
                age = ?, gender = ?, height = ?, weight = ?, goal = ?,
                diet_preference = ?, activity_level = ?, workout_time = ?,
                target_calories = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (
                profile_data['age'], profile_data['gender'], profile_data['height'],
                profile_data['weight'], profile_data['goal'], profile_data['diet_preference'],
                profile_data['activity_level'], profile_data['workout_time'],
                profile_data.get('target_calories'), user_id
            ))
        else:
            # Create new profile
            cursor.execute('''
                INSERT INTO user_profiles 
                (user_id, age, gender, height, weight, goal, diet_preference, 
                 activity_level, workout_time, target_calories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, profile_data['age'], profile_data['gender'], profile_data['height'],
                profile_data['weight'], profile_data['goal'], profile_data['diet_preference'],
                profile_data['activity_level'], profile_data['workout_time'],
                profile_data.get('target_calories')
            ))
        
        conn.commit()
        conn.close()
    
    def get_user_profile(self, user_id):
        """Get user profile data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT age, gender, height, weight, goal, diet_preference,
                   activity_level, workout_time, target_calories
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'age': result[0],
                'gender': result[1],
                'height': result[2],
                'weight': result[3],
                'goal': result[4],
                'diet_preference': result[5],
                'activity_level': result[6],
                'workout_time': result[7],
                'target_calories': result[8]
            }
        return None
    
    def save_diet_plan(self, user_id, date, meal_plan):
        """Save daily diet plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing plan for the date
        cursor.execute('DELETE FROM diet_plans WHERE user_id = ? AND date = ?', (user_id, date))
        
        # Insert new meal plan
        for meal_type, items in meal_plan.items():
            if isinstance(items, list):
                for item in items:
                    cursor.execute('''
                        INSERT INTO diet_plans 
                        (user_id, date, meal_type, food_item, calories, protein, carbs, fat)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, date, meal_type, item['name'],
                        item['calories'], item['protein'], item['carbs'], item['fat']
                    ))
            else:
                cursor.execute('''
                    INSERT INTO diet_plans 
                    (user_id, date, meal_type, food_item, calories, protein, carbs, fat)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, date, meal_type, items['name'],
                    items['calories'], items['protein'], items['carbs'], items['fat']
                ))
        
        conn.commit()
        conn.close()
    
    def save_workout_plan(self, user_id, date, workout_plan):
        """Save daily workout plan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing plan for the date
        cursor.execute('DELETE FROM workout_plans WHERE user_id = ? AND date = ?', (user_id, date))
        
        # Insert new workout plan
        for exercise in workout_plan['exercises']:
            cursor.execute('''
                INSERT INTO workout_plans 
                (user_id, date, workout_name, exercise_name, sets, reps, duration, calories_burned)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, date, workout_plan['name'], exercise['name'],
                exercise.get('sets'), str(exercise.get('reps')), 
                exercise.get('duration'), exercise.get('calories')
            ))
        
        conn.commit()
        conn.close()
    
    def log_daily_progress(self, user_id, date, weight=None, calories_consumed=None, 
                          calories_burned=None, workouts_completed=None, notes=None):
        """Log daily progress"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if log exists for the date
        cursor.execute('SELECT id FROM daily_logs WHERE user_id = ? AND date = ?', (user_id, date))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing log
            cursor.execute('''
                UPDATE daily_logs SET
                weight = COALESCE(?, weight),
                calories_consumed = COALESCE(?, calories_consumed),
                calories_burned = COALESCE(?, calories_burned),
                workouts_completed = COALESCE(?, workouts_completed),
                notes = COALESCE(?, notes)
                WHERE user_id = ? AND date = ?
            ''', (weight, calories_consumed, calories_burned, workouts_completed, notes, user_id, date))
        else:
            # Create new log
            cursor.execute('''
                INSERT INTO daily_logs 
                (user_id, date, weight, calories_consumed, calories_burned, workouts_completed, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, date, weight, calories_consumed, calories_burned, workouts_completed, notes))
        
        conn.commit()
        conn.close()
    
    def get_progress_data(self, user_id, days=30):
        """Get user progress data for specified number of days"""
        conn = sqlite3.connect(self.db_path)
        
        # Get daily logs
        query = '''
            SELECT date, weight, calories_consumed, calories_burned, workouts_completed
            FROM daily_logs 
            WHERE user_id = ? AND date >= date('now', '-{} days')
            ORDER BY date DESC
        '''.format(days)
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        return df
    
    def populate_food_database(self):
        """Populate food database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sample food data
        foods = [
            # Proteins
            ('Chicken Breast', 'protein', 165, 31, 0, 3.6, False),
            ('Salmon', 'protein', 208, 20, 0, 12, False),
            ('Eggs', 'protein', 155, 13, 1.1, 11, False),
            ('Greek Yogurt', 'dairy', 59, 10, 3.6, 0.4, False),
            ('Tofu', 'protein', 76, 8, 1.9, 4.8, True),
            ('Lentils', 'legume', 116, 9, 20, 0.4, True),
            ('Chickpeas', 'legume', 164, 8.9, 27, 2.6, True),
            
            # Carbohydrates
            ('Brown Rice', 'grain', 111, 2.6, 23, 0.9, True),
            ('Quinoa', 'grain', 120, 4.4, 22, 1.9, True),
            ('Oats', 'grain', 68, 2.4, 12, 1.4, True),
            ('Sweet Potato', 'vegetable', 86, 1.6, 20, 0.1, True),
            ('Banana', 'fruit', 89, 1.1, 23, 0.3, True),
            ('Apple', 'fruit', 52, 0.3, 14, 0.2, True),
            
            # Vegetables
            ('Broccoli', 'vegetable', 34, 2.8, 7, 0.4, True),
            ('Spinach', 'vegetable', 23, 2.9, 3.6, 0.4, True),
            ('Carrots', 'vegetable', 41, 0.9, 10, 0.2, True),
            ('Bell Peppers', 'vegetable', 31, 1, 7, 0.3, True),
            
            # Fats
            ('Avocado', 'fruit', 160, 2, 9, 15, True),
            ('Almonds', 'nuts', 579, 21, 22, 50, True),
            ('Olive Oil', 'oil', 884, 0, 0, 100, True),
            ('Peanut Butter', 'nuts', 588, 25, 20, 50, True)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO food_database 
            (name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_vegan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', foods)
        
        conn.commit()
        conn.close()
        print("Food database populated successfully!")
    
    def populate_exercise_database(self):
        """Populate exercise database with sample data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sample exercise data
        exercises = [
            ('Push-ups', 'strength', 'chest,triceps,shoulders', 'bodyweight', 'beginner', 8, 
             'Keep your body straight, lower chest to ground, push back up'),
            ('Squats', 'strength', 'legs,glutes', 'bodyweight', 'beginner', 10,
             'Feet shoulder-width apart, lower hips back and down, return to standing'),
            ('Plank', 'strength', 'core', 'bodyweight', 'beginner', 5,
             'Hold body straight from head to heels, engage core muscles'),
            ('Lunges', 'strength', 'legs,glutes', 'bodyweight', 'beginner', 9,
             'Step forward, lower hips until both knees at 90 degrees, return to start'),
            ('Burpees', 'strength', 'full_body', 'bodyweight', 'intermediate', 12,
             'Squat down, jump back to plank, do push-up, jump feet forward, jump up'),
            ('Mountain Climbers', 'cardio', 'core,cardio', 'bodyweight', 'intermediate', 11,
             'Start in plank, alternate bringing knees to chest rapidly'),
            ('Jump Squats', 'cardio', 'legs,cardio', 'bodyweight', 'intermediate', 13,
             'Perform squat then jump explosively, land softly and repeat'),
            ('Running', 'cardio', 'cardio', 'none', 'beginner', 12,
             'Maintain steady pace, land on midfoot, keep posture upright'),
            ('Cycling', 'cardio', 'cardio', 'bicycle', 'beginner', 8,
             'Maintain steady cadence, adjust resistance as needed'),
            ('Jump Rope', 'cardio', 'cardio', 'jump_rope', 'intermediate', 13,
             'Keep elbows close to body, rotate wrists, land softly on balls of feet')
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO exercise_database 
            (name, category, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', exercises)
        
        conn.commit()
        conn.close()
        print("Exercise database populated successfully!")
    
    def create_sample_user(self):
        """Create a sample user for testing"""
        user_id = self.create_user('demo@example.com', 'password123', 'Demo User')
        
        if user_id:
            # Create sample profile
            profile_data = {
                'age': 28,
                'gender': 'male',
                'height': 175,
                'weight': 75,
                'goal': 'weight-loss',
                'diet_preference': 'non-vegan',
                'activity_level': 'moderate',
                'workout_time': '30-45',
                'target_calories': 2000
            }
            
            self.save_user_profile(user_id, profile_data)
            
            # Create sample daily logs for the past week
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                self.log_daily_progress(
                    user_id, date,
                    weight=75 - i * 0.1,  # Gradual weight loss
                    calories_consumed=1800 + (i * 50),
                    calories_burned=300 + (i * 20),
                    workouts_completed=1 if i < 6 else 0
                )
            
            print(f"Sample user created with ID: {user_id}")
            print("Email: demo@example.com")
            print("Password: password123")
            
            return user_id
        else:
            print("Sample user already exists!")
            return None


def main():
    """Main function to set up the database"""
    print("=== Database Setup for AI Diet and Workout System ===")
    
    # Initialize database
    db = DatabaseManager()
    
    # Populate reference data
    print("\nPopulating food database...")
    db.populate_food_database()
    
    print("Populating exercise database...")
    db.populate_exercise_database()
    
    print("Creating sample user...")
    db.create_sample_user()
    
    print("\n✓ Database setup completed successfully!")
    print("Database file: fitness_app.db")
    print("\nYou can now:")
    print("1. Run the web application")
    print("2. Login with demo@example.com / password123")
    print("3. View sample data and test the system")

if __name__ == "__main__":
    main()
