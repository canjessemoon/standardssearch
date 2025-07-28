@echo off
echo Starting Document Search Tool Backend...
echo ====================================

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Start the Flask application
echo Starting Flask server...
echo Backend will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app\main.py

pause
