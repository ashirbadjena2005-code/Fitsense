# 🤖 Gemini 2.5 Flash Integration Setup Guide

This guide will help you integrate Gemini 2.5 Flash with your AI Diet and Workout Recommendation System, replacing the traditional ML models with AI-powered recommendations.

## 🚀 **What's Changed**

### **Before (Traditional ML)**
- K-Means clustering for diet recommendations
- Decision Tree for diet preferences
- Random Forest for calorie predictions
- Rule-based workout generation

### **After (Gemini 2.5 Flash)**
- AI-powered diet plan generation
- Intelligent workout recommendations
- Natural language calorie predictions
- Dynamic, context-aware responses

## 📋 **Prerequisites**

1. **Google AI Studio Account**: Get your free API key
2. **Python 3.8+**: Already installed
3. **Internet Connection**: Required for API calls

## 🔑 **Step 1: Get Your Gemini API Key**

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" in the left sidebar
4. Create a new API key
5. Copy the API key (starts with `AIza...`)

## ⚙️ **Step 2: Configure Your Environment**

### **Option A: Environment Variable (Recommended)**
```bash
# Windows
set GEMINI_API_KEY=your-api-key-here

# Linux/Mac
export GEMINI_API_KEY=your-api-key-here
```

### **Option B: .env File**
1. Open the `.env` file in your project root
2. Update the line:
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

## 📦 **Step 3: Install Dependencies**

```bash
# Install the new Gemini dependency
pip install google-generativeai==0.8.3

# Or reinstall all requirements
pip install -r requirements.txt
```

## 🧪 **Step 4: Test the Integration**

Run the test script to verify everything is working:

```bash
python test_gemini_integration.py
```

**Expected Output:**
```
🤖 Testing Gemini 2.5 Flash Integration
==================================================
✅ API Key found: AIzaSyC...
✅ Gemini service initialized successfully!

🧪 Testing Diet Plan Generation...
✅ Diet plan generated successfully!
   Target Calories: 2200
   Macros: {'protein': 150, 'carbs': 200, 'fat': 70}
   Meals: ['breakfast', 'lunch', 'dinner']

🏋️ Testing Workout Plan Generation...
✅ Workout plan generated successfully!
   Name: Full Body HIIT Workout
   Duration: 30 minutes
   Exercises: 6

🔥 Testing Calorie Prediction...
✅ Calorie prediction successful: 350 calories

🎉 All tests passed! Gemini integration is working correctly.
```

## 🚀 **Step 5: Start Your Application**

```bash
# Start the API server
python backend/api_server.py

# In another terminal, start the frontend
npm run dev
```

## 🎯 **What You'll Get**

### **Enhanced Diet Plans**
- **Natural Language Descriptions**: Detailed meal explanations
- **Personalized Recommendations**: Context-aware suggestions
- **Flexible Responses**: Adapts to unique user needs
- **Nutritional Insights**: AI-powered macro calculations

### **Intelligent Workouts**
- **Dynamic Exercise Selection**: Based on user context
- **Detailed Instructions**: Step-by-step exercise guidance
- **Equipment Recommendations**: What you need for each workout
- **Progression Tips**: How to advance over time

### **Accurate Calorie Predictions**
- **Context-Aware Calculations**: Considers all user factors
- **Detailed Explanations**: Why the prediction was made
- **Factor Analysis**: What influenced the calculation

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Required
GEMINI_API_KEY=your-api-key-here

# Optional
GEMINI_MODEL=gemini-2.0-flash-exp  # Default model
GEMINI_TEMPERATURE=0.7             # Response creativity (0-1)
GEMINI_MAX_TOKENS=1000             # Response length limit
```

### **Fallback Behavior**
- If Gemini API is unavailable, the system automatically falls back to traditional ML models
- No data loss or service interruption
- Seamless user experience

## 🐛 **Troubleshooting**

### **Common Issues**

1. **"GEMINI_API_KEY not found"**
   - Check your environment variables
   - Verify the .env file is in the project root
   - Restart your terminal/IDE

2. **"Failed to initialize Gemini"**
   - Check your internet connection
   - Verify your API key is correct
   - Check if you have API quota remaining

3. **"No JSON found in Gemini response"**
   - This is normal - the system will use fallback methods
   - Check the logs for more details

### **Debug Mode**
Enable debug logging to see detailed API interactions:

```bash
export LOG_LEVEL=DEBUG
python backend/api_server.py
```

## 📊 **Performance Comparison**

| Feature | Traditional ML | Gemini 2.5 Flash |
|---------|----------------|-------------------|
| **Accuracy** | 85-97% | 95%+ (estimated) |
| **Flexibility** | Fixed algorithms | Dynamic responses |
| **Personalization** | Limited | Highly personalized |
| **Maintenance** | Requires retraining | No retraining needed |
| **Response Time** | <100ms | 1-3 seconds |
| **Cost** | Free | Pay-per-use |

## 🎉 **Benefits of Gemini Integration**

1. **No Model Training**: Skip the complex ML pipeline
2. **Better Personalization**: AI understands context and nuance
3. **Easier Updates**: Just update prompts, not models
4. **Natural Language**: More human-like recommendations
5. **Scalability**: Handles any number of users without retraining

## 🔄 **Rollback Plan**

If you need to revert to traditional ML models:

1. Comment out the Gemini service calls in `ml_models.py`
2. Uncomment the original ML model code
3. Ensure your trained models are in the `models/` directory
4. Restart the application

## 📚 **Next Steps**

1. **Customize Prompts**: Modify the prompts in `gemini_service.py` for your specific needs
2. **Add More Features**: Extend the service with additional AI capabilities
3. **Monitor Usage**: Track API usage and costs
4. **Optimize Responses**: Fine-tune prompts for better results

## 🆘 **Support**

- **API Documentation**: [Google AI Studio Docs](https://ai.google.dev/docs)
- **Community**: [Google AI Community](https://discuss.ai.google.dev/)
- **Issues**: Check the project's GitHub issues

---

**Ready to get started?** Run `python test_gemini_integration.py` to test your setup! 🚀
