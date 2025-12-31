#!/bin/bash

# Hoax Detection Backend Runner Script

echo "=== Hoax Detection News App - Backend ==="
echo "Starting FastAPI server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f ".dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch .dependencies_installed
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
    exit 1
fi

# Check if Firebase credentials exist
if [ ! -f "firebase-credentials.json" ]; then
    echo "Error: firebase-credentials.json not found"
    echo "Please download it from Firebase Console and place it in the backend directory"
    exit 1
fi

# Run the server
echo "Starting server on http://localhost:8000"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
