#!/bin/bash

# Start the FastAPI backend server

echo "🚀 Starting Video Analysis Backend..."

# Check if we're in the correct directory
if [ ! -f "backend/main.py" ]; then
    echo "❌ Error: Please run this script from the web-app directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source ../.venv/bin/activate

cd backend

# Check if required directories exist
mkdir -p uploads results temp

echo "🔧 Starting FastAPI server..."
echo "📡 Backend will be available at: http://localhost:8000"
echo "📖 API documentation will be available at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the server
python main.py 