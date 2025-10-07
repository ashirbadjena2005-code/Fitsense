#!/bin/bash

echo "🚀 AI Diet & Workout System - VS Code Installation"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8+ from python.org and try again."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "setup_environment.py" ]; then
    echo "❌ setup_environment.py not found!"
    echo "Please make sure you're in the project root directory."
    exit 1
fi

echo "🔧 Starting installation and setup..."
echo "This may take a few minutes..."

# Run the setup
python3 setup_environment.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Open this folder in VS Code"
    echo "2. Press F5 to start debugging, or"
    echo "3. Run: ./run_all.sh"
    echo ""
    echo "🌐 Demo account:"
    echo "   Email: demo@example.com"
    echo "   Password: password123"
else
    echo "❌ Installation failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi
