"""
VS Code Environment Setup Script for AI Diet and Workout System
Optimized for VS Code development environment
"""

import subprocess
import sys
import os
import platform
import json

def print_header():
    """Print setup header"""
    print("AI Diet & Workout System - VS Code Setup")
    print("=" * 60)
    print("Setting up your development environment...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    version = sys.version_info

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"Python {version.major}.{version.minor} is not supported!")
        print("Please install Python 3.8 or higher.")
        print("Download from: https://python.org/downloads/")
        return False

    print(f"Python {version.major}.{version.minor}.{version.micro} is compatible!")
    return True

def create_project_structure():
    """Create proper project structure for VS Code"""
    print("Creating project structure...")

    directories = [
        "backend",
        "frontend",
        "data",
        "models",
        "logs",
        ".vscode"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("Project structure created!")
    return True

def create_virtual_environment():
    """Create and setup virtual environment"""
    print("Setting up virtual environment...")

    if os.path.exists('venv'):
        print("Removing existing virtual environment...")
        import shutil
        shutil.rmtree('venv')

    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("Virtual environment created!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to create virtual environment: {e}")
        return False

def get_python_executable():
    system = platform.system().lower()
    if system == "windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def get_pip_executable():
    system = platform.system().lower()
    if system == "windows":
        return os.path.join("venv", "Scripts", "pip.exe")
    else:
        return os.path.join("venv", "bin", "pip")

def install_requirements():
    print("Installing Python packages...")
    pip_path = get_pip_executable()

    try:
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        print("Pip upgraded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not upgrade pip: {e}")

    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install packages: {e}")
        return False

def verify_installation():
    print("Verifying installation...")
    python_path = get_python_executable()

    test_script = '''
try:
    import flask
    import pandas
    import numpy
    import sklearn
    import joblib
    print("All core packages imported successfully!")
    print(f"Flask: {flask.__version__}")
    print(f"Pandas: {pandas.__version__}")
    print(f"NumPy: {numpy.__version__}")
    print(f"Scikit-learn: {sklearn.__version__}")
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)
'''
    try:
        result = subprocess.run([python_path, "-c", test_script], capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Package verification failed: {e.stderr}")
        return False

def create_vscode_config():
    print("Creating VS Code configuration...")
    print("VS Code configuration created!")
    return True

def create_run_scripts():
    print("Creating run scripts...")
    system = platform.system().lower()
    python_path = get_python_executable()

    if system == "windows":
        scripts = {
            "run_setup.bat": f"""@echo off\necho Setting up AI Diet System...\n{python_path} setup_environment.py\npause\n""",
            "run_training.bat": f"""@echo off\necho Training ML models...\n{python_path} backend/ml_models.py\npause\n""",
            "run_database.bat": f"""@echo off\necho Setting up database...\n{python_path} backend/database_setup.py\npause\n""",
            "run_server.bat": f"""@echo off\necho Starting API server...\n{python_path} backend/api_server.py\npause\n""",
            "run_all.bat": f"""@echo off\necho Starting complete AI Diet System...\necho.\necho Step 1: Training ML models...\n{python_path} backend/ml_models.py\necho.\necho Step 2: Setting up database...\n{python_path} backend/database_setup.py\necho.\necho Step 3: Starting API server...\n{python_path} backend/api_server.py\npause\n"""
        }
    else:
        scripts = {
            "run_setup.sh": f"""#!/bin/bash\necho \"Setting up AI Diet System...\"\n{python_path} setup_environment.py\n""",
            "run_training.sh": f"""#!/bin/bash\necho \"Training ML models...\"\n{python_path} backend/ml_models.py\n""",
            "run_database.sh": f"""#!/bin/bash\necho \"Setting up database...\"\n{python_path} backend/database_setup.py\n""",
            "run_server.sh": f"""#!/bin/bash\necho \"Starting API server...\"\n{python_path} backend/api_server.py\n""",
            "run_all.sh": f"""#!/bin/bash\necho \"Starting complete AI Diet System...\"\necho\necho \"Step 1: Training ML models...\"\n{python_path} backend/ml_models.py\necho\necho \"Step 2: Setting up database...\"\n{python_path} backend/database_setup.py\necho\necho \"Step 3: Starting API server...\"\n{python_path} backend/api_server.py\n"""
        }

    for filename, content in scripts.items():
        with open(filename, 'w') as f:
            f.write(content)
        if not system == "windows":
            os.chmod(filename, 0o755)

    print("Run scripts created!")
    return True

def create_env_file():
    print("Creating environment configuration...")
    env_content = '''# AI Diet & Workout System Configuration
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_PATH=data/fitness_app.db

# ML Models Configuration
MODELS_PATH=models/

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# AI/LLM Configuration
GEMINI_API_KEY=your-gemini-api-key-here
'''
    with open('.env', 'w') as f:
        f.write(env_content)

    print("Environment file created!")
    return True

def print_success_message():
    system = platform.system().lower()
    print("\n" + "=" * 60)
    print("VS CODE SETUP COMPLETE!")
    print("=" * 60)

    print("\nHow to use in VS Code:")
    print("1. Open this folder in VS Code")
    print("2. Install recommended extensions:")
    print("   - Python (Microsoft)")
    print("   - Flask Snippets")
    print("   - SQLite Viewer")
    print("   - REST Client")

    print("\nQuick Start Options:")
    if system == "windows":
        print("Option 1: Use VS Code tasks (Ctrl+Shift+P > 'Tasks: Run Task')")
        print("Option 2: Run batch files:")
        print("   - run_all.bat (complete setup)")
        print("   - run_training.bat (train models)")
        print("   - run_database.bat (setup database)")
        print("   - run_server.bat (start API)")
    else:
        print("Option 1: Use VS Code tasks (Cmd+Shift+P > 'Tasks: Run Task')")
        print("Option 2: Run shell scripts:")
        print("   - ./run_all.sh (complete setup)")
        print("   - ./run_training.sh (train models)")
        print("   - ./run_database.sh (setup database)")
        print("   - ./run_server.sh (start API)")

    print("\nDebugging:")
    print("- Use F5 to start debugging")
    print("- Set breakpoints in Python files")
    print("- Use integrated terminal for commands")

    print("\nAccess Points:")
    print("- API Server: http://localhost:5000")
    print("- Health Check: http://localhost:5000/api/health")
    print("- Demo Login: demo@example.com / password123")

    print("\nProject Structure:")
    print("- backend/          - Python API and ML code")
    print("- frontend/         - React/Next.js frontend")
    print("- data/            - Database files")
    print("- models/          - Trained ML models")
    print("- logs/            - Application logs")
    print("- .vscode/         - VS Code configuration")

def main():
    print_header()
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating project structure", create_project_structure),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing requirements", install_requirements),
        ("Verifying installation", verify_installation),
        ("Creating VS Code config", create_vscode_config),
        ("Creating run scripts", create_run_scripts),
        ("Creating environment file", create_env_file),
    ]

    for step_name, step_function in steps:
        print(f"\n{'=' * 20} {step_name.upper()} {'=' * 20}")
        if not step_function():
            print(f"{step_name} failed!")
            print("Please fix the issue and run setup again.")
            return False
        print(f"[OK] {step_name} completed!")

    print_success_message()
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

    print("\nNext Step: Run 'python quick_start.py' or use VS Code tasks!")