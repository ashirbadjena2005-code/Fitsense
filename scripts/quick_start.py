"""
Quick Start Script - One-click setup and launch
This script handles everything: environment setup, model training, database setup, and server launch
"""

import subprocess
import sys
import os
import time
import platform

def run_setup():
    """Run the environment setup"""
    print("🔧 Setting up environment...")
    result = subprocess.run([sys.executable, "scripts/setup_environment.py"], 
                          capture_output=False, text=True)
    return result.returncode == 0

def run_with_venv(script_path):
    """Run a script with the virtual environment"""
    system = platform.system().lower()
    
    if system == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    return subprocess.run([python_path, script_path], capture_output=False, text=True)

def main():
    """Main quick start function"""
    print("🚀 AI Diet & Workout System - Quick Start")
    print("="*60)
    print("This will set up everything and start the system!")
    print("Please wait, this may take a few minutes...")
    
    # Step 1: Environment setup
    print("\n📦 Step 1: Setting up environment...")
    if not run_setup():
        print("❌ Environment setup failed!")
        return False
    
    # Step 2: Train ML models
    print("\n🤖 Step 2: Training ML models...")
    result = run_with_venv("scripts/ml_models.py")
    if result.returncode != 0:
        print("❌ ML model training failed!")
        return False
    
    # Step 3: Setup database
    print("\n🗄️ Step 3: Setting up database...")
    result = run_with_venv("scripts/database_setup.py")
    if result.returncode != 0:
        print("❌ Database setup failed!")
        return False
    
    # Step 4: Start server
    print("\n🌐 Step 4: Starting API server...")
    print("Server will start in 3 seconds...")
    time.sleep(3)
    
    print("\n" + "="*60)
    print("🎉 SYSTEM READY!")
    print("="*60)
    print("🌐 API Server: http://localhost:5000")
    print("👤 Demo Login: demo@example.com / password123")
    print("📚 Check README.md for more information")
    print("="*60)
    
    # Start the server (this will block)
    result = run_with_venv("scripts/api_server.py")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
