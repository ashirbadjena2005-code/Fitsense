"""
Environment Setup Script for AI Diet and Workout System
This script installs all required dependencies and sets up the environment.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported!")
        print("Please install Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("🏗️ Setting up virtual environment...")
    
    # Check if venv already exists
    if os.path.exists('venv'):
        print("📁 Virtual environment already exists!")
        return True
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    print("✅ Virtual environment created successfully!")
    return True

def get_activation_command():
    """Get the correct activation command for the platform"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    # Get the correct pip path
    system = platform.system().lower()
    if system == "windows":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_path} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def verify_installation():
    """Verify that all packages are installed correctly"""
    print("🔍 Verifying installation...")
    
    # Get the correct python path
    system = platform.system().lower()
    if system == "windows":
        python_path = "venv\\Scripts\\python"
    else:
        python_path = "venv/bin/python"
    
    test_script = """
import flask
import pandas
import numpy
import sklearn
import joblib
print("✅ All packages imported successfully!")
"""
    
    try:
        result = subprocess.run([python_path, "-c", test_script], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package verification failed: {e.stderr}")
        return False

def create_activation_scripts():
    """Create convenient activation scripts"""
    print("📝 Creating activation scripts...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch file
        batch_content = """@echo off
echo Activating AI Diet System environment...
call venv\\Scripts\\activate
echo Environment activated! You can now run:
echo   python scripts/api_server.py
echo   python scripts/ml_models.py
echo   python scripts/database_setup.py
cmd /k
"""
        with open("activate_env.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created activate_env.bat")
        
    else:
        # Unix shell script
        shell_content = """#!/bin/bash
echo "Activating AI Diet System environment..."
source venv/bin/activate
echo "Environment activated! You can now run:"
echo "  python scripts/api_server.py"
echo "  python scripts/ml_models.py"
echo "  python scripts/database_setup.py"
bash
"""
        with open("activate_env.sh", "w") as f:
            f.write(shell_content)
        
        # Make executable
        os.chmod("activate_env.sh", 0o755)
        print("✅ Created activate_env.sh")

def create_run_scripts():
    """Create scripts to run the application"""
    print("📝 Creating run scripts...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows run script
        run_content = """@echo off
echo Starting AI Diet and Workout System...
call venv\\Scripts\\activate
echo Training ML models...
python scripts/ml_models.py
echo Setting up database...
python scripts/database_setup.py
echo Starting API server...
python scripts/api_server.py
pause
"""
        with open("run_system.bat", "w") as f:
            f.write(run_content)
        print("✅ Created run_system.bat")
        
    else:
        # Unix run script
        run_content = """#!/bin/bash
echo "Starting AI Diet and Workout System..."
source venv/bin/activate
echo "Training ML models..."
python scripts/ml_models.py
echo "Setting up database..."
python scripts/database_setup.py
echo "Starting API server..."
python scripts/api_server.py
"""
        with open("run_system.sh", "w") as f:
            f.write(run_content)
        
        # Make executable
        os.chmod("run_system.sh", 0o755)
        print("✅ Created run_system.sh")

def print_instructions():
    """Print final instructions"""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("🎉 ENVIRONMENT SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    
    if system == "windows":
        print("1. Run the complete system:")
        print("   run_system.bat")
        print("\n2. Or activate environment manually:")
        print("   activate_env.bat")
        print("   Then run individual scripts:")
        print("   python scripts/ml_models.py")
        print("   python scripts/database_setup.py")
        print("   python scripts/api_server.py")
    else:
        print("1. Run the complete system:")
        print("   ./run_system.sh")
        print("\n2. Or activate environment manually:")
        print("   ./activate_env.sh")
        print("   Then run individual scripts:")
        print("   python scripts/ml_models.py")
        print("   python scripts/database_setup.py")
        print("   python scripts/api_server.py")
    
    print("\n🌐 Access the application:")
    print("   API Server: http://localhost:5000")
    print("   Demo Login: demo@example.com / password123")
    
    print("\n📁 Project Structure:")
    print("   scripts/          - Python backend scripts")
    print("   venv/            - Virtual environment")
    print("   requirements.txt - Python dependencies")
    print("   *.db            - SQLite database files")
    print("   *.pkl           - Trained ML models")

def main():
    """Main setup function"""
    print("🚀 AI Diet & Workout System - Environment Setup")
    print("="*60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing requirements", install_requirements),
        ("Verifying installation", verify_installation),
        ("Creating activation scripts", create_activation_scripts),
        ("Creating run scripts", create_run_scripts),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n{'='*20} {step_name.upper()} {'='*20}")
        
        if not step_function():
            failed_steps.append(step_name)
            print(f"❌ {step_name} failed!")
            break
        else:
            print(f"✅ {step_name} completed!")
    
    if failed_steps:
        print(f"\n❌ SETUP FAILED at: {failed_steps[-1]}")
        print("Please fix the issues and run the setup again.")
        return False
    else:
        print_instructions()
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
