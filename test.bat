@echo off
REM Adaptive Testing Engine - Test Runner for Windows

echo ========================================
echo   Running Tests
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

echo [INFO] Running pytest with coverage...
echo.

REM Run tests
pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

if errorlevel 1 (
    echo.
    echo [WARNING] Some tests failed
) else (
    echo.
    echo [OK] All tests passed!
)

echo.
echo Coverage report generated in: htmlcov\index.html
echo.
echo Would you like to view the coverage report? (Y/N)
set /p VIEW_REPORT="Enter choice: "

if /i "%VIEW_REPORT%"=="Y" (
    start htmlcov\index.html
)

echo.
pause
