# 🚀 Quick Start Guide

## One-Click Installation

### Windows
1. Double-click `install.bat`
2. Wait for setup to complete
3. Access the system at http://localhost:5000

### Linux/Mac
1. Run `chmod +x install.sh && ./install.sh`
2. Wait for setup to complete  
3. Access the system at http://localhost:5000

## Manual Installation

### Step 1: Setup Environment
\`\`\`bash
python scripts/setup_environment.py
\`\`\`

### Step 2: Activate Environment
\`\`\`bash
# Windows
activate_env.bat

# Linux/Mac
./activate_env.sh
\`\`\`

### Step 3: Run System
\`\`\`bash
# Windows
run_system.bat

# Linux/Mac
./run_system.sh
\`\`\`

## Demo Account
- **Email**: demo@example.com
- **Password**: password123

## Troubleshooting

### Common Issues

1. **Python not found**
   - Install Python 3.8+ from python.org
   - Make sure Python is in your PATH

2. **Permission denied (Linux/Mac)**
   \`\`\`bash
   chmod +x install.sh
   chmod +x activate_env.sh
   chmod +x run_system.sh
   \`\`\`

3. **Port already in use**
   - Change port in `scripts/api_server.py` (line with `app.run`)
   - Or kill the process using port 5000

4. **Module not found errors**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt` manually

### Getting Help

1. Check the main README.md
2. Verify all files are present
3. Ensure Python 3.8+ is installed
4. Try running scripts individually to isolate issues

## Next Steps

After successful installation:

1. **Explore the API**: Visit http://localhost:5000/api/health
2. **Test with demo account**: Login with demo@example.com
3. **Deploy frontend**: Use the provided Next.js application
4. **Customize**: Modify scripts to fit your needs
5. **Deploy to production**: Use Railway, Render, or similar platforms

## File Structure

\`\`\`
ai-fitness-app/
├── scripts/
│   ├── setup_environment.py    # Environment setup
│   ├── quick_start.py         # One-click installer
│   ├── ml_models.py           # ML model training
│   ├── database_setup.py      # Database initialization
│   └── api_server.py          # Flask API server
├── requirements.txt           # Python dependencies
├── install.sh                # Linux/Mac installer
├── install.bat               # Windows installer
├── activate_env.sh           # Environment activation (Unix)
├── activate_env.bat          # Environment activation (Windows)
├── run_system.sh             # System launcher (Unix)
├── run_system.bat            # System launcher (Windows)
└── README.md                 # Full documentation
\`\`\`

Happy coding! 🎉
