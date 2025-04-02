@echo off
echo Setting up Kids Edu App...

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed. Please install Python 3.6+ from python.org.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies. Check your internet connection or pip.
    pause
    exit /b 1
)

:: Run the app
echo Starting the app...
python app.py
pause