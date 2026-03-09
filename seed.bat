@echo off
REM Adaptive Testing Engine - Database Seeding Script for Windows

echo ========================================
echo   Database Seeding
echo ========================================
echo.

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo [INFO] Starting database seeding...
echo.

REM Run the seeding script
python scripts\seed_database.py

if errorlevel 1 (
    echo.
    echo [ERROR] Database seeding failed
    echo.
    echo Possible issues:
    echo   - MongoDB is not running
    echo   - Incorrect connection string in .env
    echo   - Network connectivity issues
    echo.
    echo For MongoDB Atlas:
    echo   1. Go to https://cloud.mongodb.com
    echo   2. Create a free cluster
    echo   3. Get connection string
    echo   4. Update MONGODB_URI in .env
    echo.
    echo For local MongoDB:
    echo   1. Download from https://www.mongodb.com/try/download/community
    echo   2. Install and start MongoDB service
    echo   3. Use: MONGODB_URI=mongodb://localhost:27017
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Database Seeding Complete!
echo ========================================
echo.
echo You can now run the application using:
echo   - Double-click: run.bat
echo   - Or in terminal: python -m uvicorn app.main:app --reload
echo.
pause
