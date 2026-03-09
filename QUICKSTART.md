# 🚀 Quick Start Guide

Get the Adaptive Testing Engine running in 5 minutes!

## Prerequisites

✅ Python 3.11 or higher  
✅ MongoDB (local or Atlas account)  
✅ Git

## Installation Steps

### 1. Get the Code

```bash
cd adaptive-testing-engine
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example config
cp .env.example .env

# Edit with your settings (optional for local testing)
nano .env  # or use your favorite editor
```

**Minimum configuration for local testing:**
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=adaptive_testing
```

### 4. Set Up Database

**Option A: Local MongoDB**
```bash
# Install MongoDB locally
# Then run:
mongod
```

**Option B: MongoDB Atlas (Free Cloud)**
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free account
3. Create cluster (free tier)
4. Get connection string
5. Update `MONGODB_URI` in `.env`

### 5. Seed Sample Data

```bash
python scripts/seed_database.py
```

You should see:
```
✅ Inserted 20 questions
✅ Indexes created
📊 Question Distribution: ...
```

### 6. Start the Server

```bash
# Option 1: Direct start
uvicorn app.main:app --reload

# Option 2: Use the convenience script
./run.sh
```

### 7. Test It Out!

Open your browser to:
- **Interactive API docs**: http://localhost:8000/docs
- **API health check**: http://localhost:8000/api/health
- **System stats**: http://localhost:8000/api/stats

## First API Test

### Using the Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Click on "POST /api/sessions"
3. Click "Try it out"
4. Click "Execute"
5. Copy the `session_id` from the response

### Using curl

```bash
# Create a session
curl -X POST "http://localhost:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{"test_type": "GRE", "max_questions": 5}'

# Response will include session_id
# Example: "session_id": "sess_abc123"

# Get first question (replace with your session_id)
curl "http://localhost:8000/api/sessions/sess_abc123/next-question"

# Submit an answer (use question_id from previous response)
curl -X POST "http://localhost:8000/api/sessions/sess_abc123/answers" \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "YOUR_QUESTION_ID",
    "user_answer": "30"
  }'
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Database connection error"
```bash
# Check MongoDB is running
# For local: mongod should be running
# For Atlas: check your connection string in .env

# Verify connection
python scripts/seed_database.py verify
```

### "No questions found"
```bash
# Reseed the database
python scripts/seed_database.py
```

### Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8080
```

## Next Steps

✅ **Read the full README.md** for detailed documentation  
✅ **Check API_EXAMPLES.md** for usage examples  
✅ **Run tests**: `pytest`  
✅ **Enable AI features**: Add OpenAI or Anthropic API key to `.env`

## Key Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/sessions` | POST | Create new test session |
| `/api/sessions/{id}/next-question` | GET | Get next adaptive question |
| `/api/sessions/{id}/answers` | POST | Submit answer |
| `/api/sessions/{id}/learning-plan` | GET | Get AI study plan |
| `/api/health` | GET | Health check |
| `/docs` | GET | Interactive API docs |

## Questions?

- 📚 Read the [README.md](README.md)
- 🔍 Check the [API Examples](API_EXAMPLES.md)
- 🐛 Found a bug? Open an issue

Happy testing! 🎯
