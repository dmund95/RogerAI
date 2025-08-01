#!/bin/bash

# Video Analysis Web Application Setup Script

set -e

echo "🚀 Setting up Video Analysis Web Application..."

# Check if we're in the correct directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Please run this script from the web-app directory"
    exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check Node.js version
echo "📦 Checking Node.js version..."
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo "Node.js version: $node_version"
else
    echo "❌ Error: Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Setup Backend
echo "🔧 Setting up Backend..."

# Activate virtual environment
source ../.venv/bin/activate

cd backend

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete!"

# Go back to web-app directory
cd ..

# Setup Frontend
echo "🎨 Setting up Frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

# Go back to web-app directory
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p backend/results
mkdir -p backend/temp

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Gemini API key from: https://ai.google.dev/"
echo "2. Start the backend server:"
echo "   cd backend && source .venv/bin/activate && python main.py"
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend && npm start"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "🔗 Backend API will be available at: http://localhost:8000"
echo "🔗 Frontend will be available at: http://localhost:3000" 