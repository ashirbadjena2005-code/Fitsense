"""
Quick Start Script - VS Code Optimized
One-click setup and launch for VS Code development
"""

import subprocess
import sys
import os
import time
import platform
from pathlib import Path

def print_header():
    """Print startup header"""
    print("🚀 AI Diet & Workout System - Quick Start")
    print("=" * 60)
    print("VS Code optimized version")
    print("This will set up everything and start the system!")
    print()

def check_environment():
    """Check if environment is set up"""
    python_path = get_python_executable()
    
    if not os.path.exists(python_path):
        print("❌ Virtual environment not found!")
        print("Please run 'python setup_environment.py' first.")
        return False
    
    print("✅ Virtual environment found!")
    return True

def get_python_executable():
    """Get the correct Python executable path"""
    system = platform.system().lower()
    
    if system == "windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def run_with_venv(script_path, description="Running script"):
    """Run a script with the virtual environment"""
    python_path = get_python_executable()
    
    print(f"🔄 {description}...")

    # Inject environment variables
    env = os.environ.copy()
    env["FLASK_ENV"] = "development"
    env["SECRET_KEY"] = "dev-key"

    try:
        result = subprocess.run([python_path, script_path], 
                                capture_output=False, text=True, check=True,
                                env=env)
        print(f"✅ {description} completed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Could not find Python executable: {python_path}")
        print("Please run setup_environment.py first.")
        return False

def setup_directories():
    """Ensure all directories exist"""
    directories = ["backend", "data", "models", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    return True

def main():
    """Main quick start function"""
    print_header()
    
    # Check if we need to run setup first
    if not check_environment():
        print("🔧 Running environment setup first...")
        if not subprocess.run([sys.executable, "setup_environment.py"]).returncode == 0:
            print("❌ Environment setup failed!")
            return False
    
    # Ensure directories exist
    setup_directories()
    
    # Step 1: Train ML models
    print("\n🤖 Step 1: Training ML models...")
    if not run_with_venv("backend/ml_models.py", "Training ML models"):
        print("❌ ML model training failed!")
        return False
    
    # Step 2: Setup database
    print("\n🗄️ Step 2: Setting up database...")
    if not run_with_venv("backend/database_setup.py", "Setting up database"):
        print("❌ Database setup failed!")
        return False
    
    # Step 3: Start server
    print("\n🌐 Step 3: Starting API server...")
    print("Server will start in 3 seconds...")
    print("Press Ctrl+C to stop the server when you're done testing.")
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM READY!")
    print("=" * 60)
    print("🌐 API Server: http://localhost:5000")
    print("🔍 Health Check: http://localhost:5000/api/health")
    print("👤 Demo Login: demo@example.com / password123")
    print("📚 Check README.md for more information")
    print("🐛 Use VS Code debugger for development")
    print("=" * 60)
    
    # Start the server (this will block)
    try:
        run_with_venv("backend/api_server.py", "Starting API server")
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user. System ready for development!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user. Run again when ready!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again.")
        sys.exit(1)
