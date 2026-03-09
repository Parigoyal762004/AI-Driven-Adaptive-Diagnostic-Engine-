@echo off
REM Quick Fix for Python 3.13 Dependency Installation Issues

echo ========================================
echo   Dependency Installation Fix
echo   For Python 3.13 on Windows
echo ========================================
echo.

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo [INFO] Upgrading pip to latest version...
python -m pip install --upgrade pip
echo.

echo [INFO] Installing wheel (for binary packages)...
pip install wheel
echo.

echo [INFO] Installing compatible package versions for Python 3.13...
echo This will use pre-built wheels that don't require Rust compilation
echo.

REM Install packages one by one with compatible versions
echo Installing FastAPI and dependencies...
pip install fastapi==0.115.6
pip install "uvicorn[standard]==0.34.0"
pip install starlette

echo Installing Pydantic (compatible version)...
pip install pydantic==2.10.6
pip install pydantic-settings==2.7.1
pip install pydantic-core

echo Installing Motor (MongoDB driver)...
pip install motor==3.6.0
pip install pymongo

echo Installing utilities...
pip install python-dotenv==1.0.1
pip install httpx==0.28.1
pip install python-multipart==0.0.20

echo Installing testing tools...
pip install pytest==8.3.4
pip install pytest-asyncio==0.25.2
pip install pytest-cov==6.0.0

echo Installing code quality tools...
pip install mypy==1.14.1
pip install ruff==0.9.3

echo Installing AI SDKs...
pip install openai==1.59.8
pip install anthropic==0.42.0

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo All packages have been installed successfully.
echo You can now run: run.bat
echo.
pause
