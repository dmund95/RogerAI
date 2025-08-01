#!/bin/bash

# Start the React frontend server

echo "🎨 Starting Video Analysis Frontend..."

# Check if we're in the correct directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: Please run this script from the web-app directory"
    exit 1
fi

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Error: Node modules not found. Please run setup.sh first."
    exit 1
fi

echo "🔧 Starting React development server..."
echo "🌐 Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the development server
npm start 