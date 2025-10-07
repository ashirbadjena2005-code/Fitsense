@echo off
echo 🚀 AI Diet ^& Workout System - VS Code Installation
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please install Python 3.8+ from python.org and try again.
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if we're in the right directory
if not exist "setup_environment.py" (
    echo ❌ setup_environment.py not found!
    echo Please make sure you're in the project root directory.
    pause
    exit /b 1
)

echo 🔧 Starting installation and setup...
echo This may take a few minutes...

REM Run the setup
python setup_environment.py

if errorlevel 1 (
    echo ❌ Installation failed!
    echo Please check the error messages above and try again.
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Open this folder in VS Code
echo 2. Press F5 to start debugging, or
echo 3. Run: run_all.bat
echo.
echo 🌐 Demo account:
echo    Email: demo@example.com
echo    Password: password123

pause
