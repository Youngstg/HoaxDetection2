@echo off

echo === Hoax Detection News App - Backend ===
echo Starting FastAPI server...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
if not exist ".dependencies_installed" (
    echo Installing dependencies...
    pip install -r requirements.txt
    type nul > .dependencies_installed
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env file with your configuration
    exit /b 1
)

REM Check if Firebase credentials exist
if not exist "firebase-credentials.json" (
    echo Error: firebase-credentials.json not found
    echo Please download it from Firebase Console and place it in the backend directory
    exit /b 1
)

REM Run the server
echo Starting server on http://localhost:8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
