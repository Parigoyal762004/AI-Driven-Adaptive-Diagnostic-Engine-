#!/bin/bash

# Adaptive Testing Engine - Startup Script

set -e

echo "🚀 Starting Adaptive Testing Engine"
echo "===================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration"
    exit 1
fi

# Check if database needs seeding
echo "🔍 Checking database..."
python -c "
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()
async def check():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    db = client[os.getenv('MONGODB_DATABASE', 'adaptive_testing')]
    count = await db.questions.count_documents({'is_active': True})
    client.close()
    return count

count = asyncio.run(check())
if count == 0:
    print('⚠️  No questions found in database!')
    print('🌱 Run: python scripts/seed_database.py')
    sys.exit(1)
else:
    print(f'✅ Found {count} active questions')
" || {
    echo "🌱 Seeding database..."
    python scripts/seed_database.py
}

# Start the application
echo ""
echo "✅ Starting FastAPI server..."
echo "📍 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
