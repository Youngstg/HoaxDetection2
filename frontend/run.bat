@echo off

echo === Hoax Detection News App - Frontend ===
echo Starting React development server...

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Dependencies not installed. Installing...
    call npm install
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found. Creating from .env.example...
    copy .env.example .env
    echo Please edit .env file if needed
)

REM Run the development server
echo Starting server on http://localhost:3000
npm run dev

pause
