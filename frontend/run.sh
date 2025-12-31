#!/bin/bash

# Hoax Detection Frontend Runner Script

echo "=== Hoax Detection News App - Frontend ==="
echo "Starting React development server..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not installed. Installing..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env file if needed"
fi

# Run the development server
echo "Starting server on http://localhost:3000"
npm run dev
