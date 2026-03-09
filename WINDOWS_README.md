# Windows Quick Start Guide

## 🪟 For Windows Users

This guide will help you get the Adaptive Testing Engine running on Windows in just a few minutes!

## 📋 Prerequisites

1. **Python 3.11 or higher**
   - Download from: https://www.python.org/downloads/
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation!

2. **MongoDB** (choose one):
   - **Option A - MongoDB Atlas** (Recommended for beginners)
     - Free cloud database
     - No installation needed
     - Sign up at: https://cloud.mongodb.com
   
   - **Option B - Local MongoDB**
     - Download from: https://www.mongodb.com/try/download/community
     - Install MongoDB Community Server
     - Start MongoDB service

## 🚀 Installation Steps

### Step 1: Extract the Project

1. Extract the `adaptive-testing-engine.zip` file
2. Open the extracted folder
3. You should see files like `setup.bat`, `run.bat`, etc.

### Step 2: Run Initial Setup

**Double-click: `setup.bat`**

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` configuration file

### Step 3: Configure Database

1. The setup will open `.env` file in Notepad
2. Update the MongoDB connection:

**For MongoDB Atlas (Cloud):**
```env
MONGODB_URI=
MONGODB_DATABASE=adaptive_testing
```

**For Local MongoDB:**
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=adaptive_testing
```

3. (Optional) Add AI API key for learning plans:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

4. Save and close Notepad

### Step 4: Seed Database with Questions

**Double-click: `seed.bat`**

This will:
- ✅ Connect to MongoDB
- ✅ Create collections and indexes
- ✅ Insert 20 sample GRE questions
- ✅ Verify the setup

### Step 5: Run the Application

**Double-click: `run.bat`**

The server will start and you'll see:
```
Starting FastAPI Server
API will be available at:
  - http://localhost:8000
  - http://localhost:8000/docs
```

### Step 6: Test the API

Open your web browser and go to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📁 Batch Scripts Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `setup.bat` | Initial setup | First time only |
| `run.bat` | Start the application | Every time you want to run |
| `seed.bat` | Seed database with questions | After database setup or reset |
| `test.bat` | Run unit tests | To verify code is working |

## 🎯 Quick Test

1. Open http://localhost:8000/docs in your browser
2. Find "POST /api/sessions" endpoint
3. Click "Try it out"
4. Click "Execute"
5. Copy the `session_id` from the response
6. Use that ID in "GET /api/sessions/{session_id}/next-question"
7. You'll get your first adaptive question!

## 🔧 Troubleshooting

### "Python is not recognized"
- ❌ Problem: Python not in PATH
- ✅ Solution: Reinstall Python and check "Add Python to PATH"

### "Failed to connect to MongoDB"
- ❌ Problem: MongoDB not running or wrong connection string
- ✅ Solution for Atlas: 
  1. Go to MongoDB Atlas dashboard
  2. Click "Connect" → "Connect your application"
  3. Copy the connection string
  4. Update in `.env` file
- ✅ Solution for Local:
  1. Start MongoDB service from Windows Services
  2. Or run `mongod` command

### "No questions found"
- ❌ Problem: Database not seeded
- ✅ Solution: Run `seed.bat`

### Port 8000 already in use
- ❌ Problem: Another application using port 8000
- ✅ Solution: Edit `run.bat` and change port:
  ```batch
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
  ```

### Dependencies installation fails
- ❌ Problem: Network issues or pip problems
- ✅ Solution:
  ```batch
  venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

## 🎓 Next Steps

1. **Read the Documentation**
   - `README.md` - Full documentation
   - `API_EXAMPLES.md` - Usage examples
   - `PROJECT_SUMMARY.md` - System overview

2. **Customize Questions**
   - Edit `scripts\gre_questions.json`
   - Add your own questions
   - Run `seed.bat` again

3. **Enable AI Features**
   - Get API key from OpenAI (https://platform.openai.com/api-keys)
   - Or Anthropic (https://console.anthropic.com/)
   - Add to `.env` file
   - Restart application

4. **Deploy to Production**
   - Read `README.md` deployment section
   - Use Railway, Render, or Heroku
   - Or containerize with Docker

## 💡 Tips

- **Keep the terminal open** when running `run.bat` - closing it stops the server
- **Press Ctrl+C** in the terminal to stop the server
- **Use `run.bat`** every time you want to start (it's smart - won't reinstall if not needed)
- **Check logs** in the terminal window for errors
- **API Docs** at `/docs` are your best friend for testing

## 📞 Getting Help

If you encounter issues:
1. Check the error message in the terminal
2. Read the troubleshooting section above
3. Check `README.md` for detailed documentation
4. Verify all prerequisites are installed

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] MongoDB running (local or Atlas)
- [ ] `setup.bat` completed successfully
- [ ] `.env` file configured
- [ ] `seed.bat` added questions
- [ ] `run.bat` starts server without errors
- [ ] http://localhost:8000/docs opens in browser

---

**You're all set!** 🎉 The Adaptive Testing Engine is now running on your Windows machine.
