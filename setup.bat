@echo off
REM Adaptive Testing Engine - Windows Setup Script

echo ========================================
echo   Adaptive Testing Engine
echo   Initial Setup
echo ========================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version
echo [OK] Python is installed
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist "venv\" (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
echo This may take a few minutes, please wait...
echo.

REM Upgrade pip first
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Check Python version
for /f "tokens=2" %%i in ('python --version') do set PYVER=%%i
echo [INFO] Python version: %PYVER%

REM Install dependencies
echo [INFO] Installing packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    echo Common issues and solutions:
    echo.
    echo 1. If you see "Rust" or "Cargo" errors:
    echo    - You're using Python 3.13+ which requires pre-built wheels
    echo    - Solution: The requirements.txt has been updated
    echo    - Try running: pip install --upgrade pip
    echo    - Then run this setup again
    echo.
    echo 2. If using Python 3.11 or 3.12:
    echo    - Use: pip install -r requirements-py311-py312.txt
    echo.
    echo 3. Network/timeout issues:
    echo    - Try: pip install --default-timeout=100 -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] All dependencies installed
echo.

REM Create .env file
echo [5/5] Setting up configuration...
if exist ".env" (
    echo [INFO] .env file already exists
    set /p OVERWRITE="Do you want to reset it? (Y/N): "
    if /i "%OVERWRITE%"=="Y" (
        copy .env.example .env >nul
        echo [OK] .env file reset from template
    )
) else (
    copy .env.example .env >nul
    echo [OK] .env file created from template
)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env file with your settings
echo      - MongoDB connection string
echo      - OpenAI or Anthropic API key (optional)
echo.
echo   2. Start MongoDB (if using local):
echo      - Download from: https://www.mongodb.com/try/download/community
echo      - Or use MongoDB Atlas (free cloud): https://cloud.mongodb.com
echo.
echo   3. Run the application:
echo      - Double-click: run.bat
echo      - Or in terminal: python -m uvicorn app.main:app --reload
echo.
echo Would you like to open .env file for editing now? (Y/N)
set /p EDIT_ENV="Enter choice: "

if /i "%EDIT_ENV%"=="Y" (
    notepad .env
)

echo.
echo ========================================
echo Press any key to exit...
pause >nul
