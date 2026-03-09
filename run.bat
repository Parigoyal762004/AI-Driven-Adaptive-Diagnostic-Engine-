@echo off
REM Adaptive Testing Engine - Windows Startup Script

echo ========================================
echo   Adaptive Testing Engine
echo   Starting Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
if not exist "venv\installed.txt" (
    echo [SETUP] Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo installed > venv\installed.txt
    echo [OK] Dependencies installed
)

echo [OK] Dependencies ready
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    if exist ".env.example" (
        echo [SETUP] Copying .env.example to .env...
        copy .env.example .env >nul
        echo.
        echo ====================================================
        echo   IMPORTANT: Please edit .env file with your
        echo   MongoDB connection string and API keys
        echo ====================================================
        echo.
        echo Opening .env file for editing...
        timeout /t 2 >nul
        notepad .env
        echo.
        echo Press any key after you've configured .env...
        pause >nul
    ) else (
        echo [ERROR] .env.example not found
        pause
        exit /b 1
    )
)

echo [OK] Configuration file ready
echo.

REM Check database connection and seed if needed
echo [CHECK] Verifying database setup...
python -c "import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; from dotenv import load_dotenv; import os; load_dotenv(); async def check(): client = AsyncIOMotorClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017')); db = client[os.getenv('MONGODB_DATABASE', 'adaptive_testing')]; count = await db.questions.count_documents({'is_active': True}); client.close(); return count; count = asyncio.run(check()); print(f'Found {count} questions'); exit(0 if count > 0 else 1)" 2>nul

if errorlevel 1 (
    echo [WARNING] No questions found in database
    echo [SETUP] Would you like to seed the database now? (Y/N^)
    set /p SEED_DB="Enter choice: "
    if /i "%SEED_DB%"=="Y" (
        echo [SETUP] Seeding database...
        python scripts\seed_database.py
        if errorlevel 1 (
            echo [ERROR] Database seeding failed
            echo Please check your MongoDB connection
            pause
            exit /b 1
        )
        echo [OK] Database seeded successfully
    ) else (
        echo [WARNING] Skipping database seeding
        echo The application may not work without questions
    )
) else (
    echo [OK] Database contains questions
)

echo.
echo ========================================
echo   Starting FastAPI Server
echo ========================================
echo.
echo API will be available at:
echo   - http://localhost:8000
echo   - http://localhost:8000/docs (Interactive API docs)
echo   - http://localhost:8000/api/health (Health check)
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

REM If we get here, server stopped
echo.
echo Server stopped.
pause
