"""
Configuration settings for AI Diet and Workout System
VS Code optimized configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'
    
    # Database Configuration (Neon DB - PostgreSQL)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Fallback PostgreSQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'fitsense_db')
    DB_USER = os.getenv('DB_USER', 'neondb_owner')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # If no DATABASE_URL, construct it from individual components
    if not DATABASE_URL:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # ML Models Configuration
    MODELS_PATH = os.getenv('MODELS_PATH', str(BASE_DIR / 'models'))
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))
    
    # CORS Configuration
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # AI/LLM Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration"""
        # Ensure directories exist
        os.makedirs(Config.MODELS_PATH, exist_ok=True)
        os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # No DATABASE_PATH needed for PostgreSQL-only config

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
