import psycopg2
import psycopg2.extras
from psycopg2 import IntegrityError
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pandas as pd

# Import configuration
from backend.config import get_config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages all database operations for the fitness application
    """
    def __init__(self, db_url):
        self.db_url = db_url

    def create_tables(self):
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL
                    );
                ''')
                # User profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        age INTEGER,
                        gender VARCHAR(10),
                        height REAL,
                        weight REAL,
                        goal VARCHAR(50),
                        diet_preference VARCHAR(50),
                        activity_level VARCHAR(50),
                        workout_time VARCHAR(50),
                        target_calories INTEGER,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                # Daily logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_logs (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        date DATE NOT NULL,
                        weight REAL,
                        calories_consumed REAL,
                        calories_burned REAL,
                        workouts_completed INTEGER DEFAULT 0,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                # Diet plans table (missing before)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS diet_plans (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        date DATE NOT NULL,
                        meal_type VARCHAR(50) NOT NULL,
                        food_item VARCHAR(255) NOT NULL,
                        calories REAL NOT NULL,
                        protein REAL NOT NULL,
                        carbs REAL NOT NULL,
                        fat REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                # Food database table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS food_database (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        calories_per_100g REAL NOT NULL,
                        protein_per_100g REAL NOT NULL,
                        carbs_per_100g REAL NOT NULL,
                        fat_per_100g REAL NOT NULL,
                        is_vegan BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                # Exercise database table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exercise_database (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) UNIQUE NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        muscle_groups VARCHAR(255) NOT NULL,
                        equipment VARCHAR(50),
                        difficulty_level VARCHAR(20) NOT NULL,
                        calories_per_minute REAL NOT NULL,
                        instructions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
                # Workout plans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS workout_plans (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL REFERENCES users(id),
                        date DATE NOT NULL,
                        workout_name VARCHAR(255) NOT NULL,
                        exercise_name VARCHAR(255) NOT NULL,
                        sets INTEGER,
                        reps VARCHAR(50),
                        duration INTEGER,
                        calories_burned REAL,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                ''')
            conn.commit()
        logger.info("Database tables created successfully!")

    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, email, password, name):
        """Create a new user account"""
        logger.info(f"Creating user account for {email}")
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cursor:
                    password_hash = self.hash_password(password)
                    cursor.execute('''
                        INSERT INTO users (email, password_hash, name)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    ''', (email, password_hash, name))
                    result = cursor.fetchone()
                    conn.commit()
                    if result:
                        user_id = result[0]
                        logger.info(f"User created successfully with ID: {user_id}")
                        return user_id
                    else:
                        logger.warning("No user ID returned after insert.")
                        return None
        except IntegrityError:
            logger.warning(f"User with email {email} already exists")
            return None

    def authenticate_user(self, email, password):
        """Authenticate user login"""
        logger.info(f"Authenticating user: {email}")
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                password_hash = self.hash_password(password)
                cursor.execute('''
                    SELECT id, name FROM users 
                    WHERE email = %s AND password_hash = %s
                ''', (email, password_hash))
                result = cursor.fetchone()
        if result:
            return {'id': result[0], 'name': result[1], 'email': email}
        else:
            logger.warning(f"Authentication failed for {email}")
            return None

    def save_user_profile(self, user_id, profile_data):
        """Save or update user profile"""
        logger.info(f"Saving profile for user ID: {user_id}")
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id FROM user_profiles WHERE user_id = %s', (user_id,))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute(
                        'UPDATE user_profiles SET age = %s, gender = %s, height = %s, weight = %s, goal = %s, diet_preference = %s, activity_level = %s, workout_time = %s, target_calories = %s, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s',
                        (
                            profile_data['age'], profile_data['gender'], profile_data['height'],
                            profile_data['weight'], profile_data['goal'], profile_data['diet_preference'],
                            profile_data['activity_level'], profile_data['workout_time'],
                            profile_data.get('target_calories'), user_id
                        )
                    )
                    logger.info(f"Profile updated for user ID: {user_id}")
                else:
                    cursor.execute(
                        'INSERT INTO user_profiles (user_id, age, gender, height, weight, goal, diet_preference, activity_level, workout_time, target_calories) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (
                            user_id, profile_data['age'], profile_data['gender'], profile_data['height'],
                            profile_data['weight'], profile_data['goal'], profile_data['diet_preference'],
                            profile_data['activity_level'], profile_data['workout_time'],
                            profile_data.get('target_calories')
                        )
                    )
                    logger.info(f"New profile created for user ID: {user_id}")
            conn.commit()

    def get_user_profile(self, user_id):
        """Get user profile data"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT age, gender, height, weight, goal, diet_preference,
                           activity_level, workout_time, target_calories
                    FROM user_profiles WHERE user_id = %s
                ''', (user_id,))
                result = cursor.fetchone()
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
        logger.info(f"Saving diet plan for user {user_id} on {date}")
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM diet_plans WHERE user_id = %s AND date = %s', (user_id, date))
                for meal_type, items in meal_plan.items():
                    if isinstance(items, list):
                        for item in items:
                            cursor.execute('''
                                INSERT INTO diet_plans 
                                (user_id, date, meal_type, food_item, calories, protein, carbs, fat)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ''', (
                                user_id, date, meal_type, item['name'],
                                item['calories'], item['protein'], item['carbs'], item['fat']
                            ))
                    else:
                        cursor.execute('''
                            INSERT INTO diet_plans 
                            (user_id, date, meal_type, food_item, calories, protein, carbs, fat)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            user_id, date, meal_type, items['name'],
                            items['calories'], items['protein'], items['carbs'], items['fat']
                        ))
            conn.commit()
        logger.info(f"Diet plan saved successfully")

    def save_workout_plan(self, user_id, date, workout_plan):
        """Save daily workout plan"""
        logger.info(f"Saving workout plan for user {user_id} on {date}")
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('DELETE FROM workout_plans WHERE user_id = %s AND date = %s', (user_id, date))
                for exercise in workout_plan['exercises']:
                    cursor.execute('''
                        INSERT INTO workout_plans 
                        (user_id, date, workout_name, exercise_name, sets, reps, duration, calories_burned)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        user_id, date, workout_plan['name'], exercise['name'],
                        exercise.get('sets'), str(exercise.get('reps')), 
                        exercise.get('duration'), exercise.get('calories')
                    ))
            conn.commit()
        logger.info(f"Workout plan saved successfully")

    def log_daily_progress(self, user_id, date, weight=None, calories_consumed=None, 
                          calories_burned=None, workouts_completed=None, notes=None):
        """Log daily progress"""
        logger.info(f"Logging progress for user {user_id} on {date}")
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id FROM daily_logs WHERE user_id = %s AND date = %s', (user_id, date))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute('''
                        UPDATE daily_logs SET
                        weight = COALESCE(%s, weight),
                        calories_consumed = COALESCE(%s, calories_consumed),
                        calories_burned = COALESCE(%s, calories_burned),
                        workouts_completed = COALESCE(%s, workouts_completed),
                        notes = COALESCE(%s, notes)
                        WHERE user_id = %s AND date = %s
                    ''', (weight, calories_consumed, calories_burned, workouts_completed, notes, user_id, date))
                else:
                    cursor.execute('''
                        INSERT INTO daily_logs 
                        (user_id, date, weight, calories_consumed, calories_burned, workouts_completed, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (user_id, date, weight, calories_consumed, calories_burned, workouts_completed, notes))
            conn.commit()
        logger.info(f"Progress logged successfully")

    def get_progress_data(self, user_id, days=30):
        """Get user progress data for specified number of days"""
        with psycopg2.connect(self.db_url) as conn:
            query = f'''
                SELECT date, weight, calories_consumed, calories_burned, workouts_completed
                FROM daily_logs 
                WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '{days} days'
                ORDER BY date DESC
            '''
            df = pd.read_sql_query(query, conn, params=(user_id,))
        return df

    def populate_food_database(self):
        """Populate food database with sample data"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                foods = [
                    ('Apple', 'fruit', 52, 0.3, 14, 0.2, True),
                    ('Chicken Breast', 'meat', 165, 31, 0, 3.6, False),
                    ('Broccoli', 'vegetable', 34, 2.8, 7, 0.4, True),
                    ('Rice', 'grain', 130, 2.7, 28, 0.3, True),
                    ('Egg', 'protein', 155, 13, 1.1, 11, False)
                ]
                for food in foods:
                    cursor.execute('''
                        INSERT INTO food_database (name, category, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, is_vegan)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    ''', food)
            conn.commit()
        logger.info("Food database populated successfully!")

    def populate_exercise_database(self):
        """Populate exercise database with sample data"""
        with psycopg2.connect(self.db_url) as conn:
            with conn.cursor() as cursor:
                exercises = [
                    ('Push-ups', 'strength', 'chest,triceps,shoulders', 'bodyweight', 'beginner', 8, 'Keep your body straight, lower chest to ground, push back up'),
                    ('Squats', 'strength', 'legs,glutes', 'bodyweight', 'beginner', 10, 'Feet shoulder-width apart, lower hips back and down, return to standing'),
                    ('Plank', 'strength', 'core', 'bodyweight', 'beginner', 5, 'Hold body straight from head to heels, engage core muscles'),
                    ('Lunges', 'strength', 'legs,glutes', 'bodyweight', 'beginner', 9, 'Step forward, lower hips until both knees at 90 degrees, return to start'),
                    ('Burpees', 'strength', 'full_body', 'bodyweight', 'intermediate', 12, 'Squat down, jump back to plank, do push-up, jump feet forward, jump up'),
                    ('Mountain Climbers', 'cardio', 'core,cardio', 'bodyweight', 'intermediate', 11, 'Start in plank, alternate bringing knees to chest rapidly'),
                    ('Jump Squats', 'cardio', 'legs,cardio', 'bodyweight', 'intermediate', 13, 'Perform squat then jump explosively, land softly and repeat'),
                    ('Running', 'cardio', 'cardio', 'none', 'beginner', 12, 'Maintain steady pace, land on midfoot, keep posture upright'),
                    ('Cycling', 'cardio', 'cardio', 'bicycle', 'beginner', 8, 'Maintain steady cadence, adjust resistance as needed'),
                    ('Jump Rope', 'cardio', 'cardio', 'jump_rope', 'intermediate', 13, 'Keep elbows close to body, rotate wrists, land softly on balls of feet')
                ]
                for ex in exercises:
                    cursor.execute('''
                        INSERT INTO exercise_database (name, category, muscle_groups, equipment, difficulty_level, calories_per_minute, instructions)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO NOTHING
                    ''', ex)
            conn.commit()
        logger.info("Exercise database populated successfully!")

    def create_sample_user(self):
        """Create a sample user for testing"""
        logger.info("Creating sample user...")
        user_id = self.create_user('demo@example.com', 'password123', 'Demo User')
        if user_id:
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
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                self.log_daily_progress(
                    user_id, date,
                    weight=75 - i * 0.1,
                    calories_consumed=1800 + (i * 50),
                    calories_burned=300 + (i * 20),
                    workouts_completed=1 if i < 6 else 0
                )
            logger.info(f"Sample user created with ID: {user_id}")
            print(f"Sample user created with ID: {user_id}")
            print("Email: demo@example.com")
            print("Password: password123")
            return user_id
        else:
            logger.info("Sample user already exists!")
            print("Sample user already exists!")
            return None

def main():
    print("=== Database Setup for AI Diet and Workout System ===")
    print("VS Code Optimized Version")
    config = get_config()
    db = DatabaseManager(config.DATABASE_URL)
    db.create_tables()
    print("\nPopulating food database...")
    db.populate_food_database()
    print("Populating exercise database...")
    db.populate_exercise_database()
    print("Creating sample user...")
    db.create_sample_user()
    print("\n✓ Database setup completed successfully!")
    print(f"Database: {getattr(config, 'DATABASE_PATH', 'PostgreSQL database')}")
    print("\nYou can now:")
    print("1. Run the web application")
    print("2. Login with demo@example.com / password123")
    print("3. View sample data and test the system")

if __name__ == '__main__':
    main() 