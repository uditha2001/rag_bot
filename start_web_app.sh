#!/bin/bash

echo "Starting RAG Bot Web Application..."
echo

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo

# Start backend server
echo "🚀 Starting FastAPI backend server..."
python web_server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Install React dependencies if needed
if [ ! -d "web_ui/node_modules" ]; then
    echo "📦 Installing React dependencies..."
    cd web_ui
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install React dependencies"
        kill $BACKEND_PID
        exit 1
    fi
    cd ..
fi

# Start frontend
echo "🎨 Starting React frontend..."
cd web_ui
npm start &
FRONTEND_PID=$!
cd ..

echo
echo "✅ RAG Bot is running!"
echo
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo
echo "Press Ctrl+C to stop all services..."

# Wait for user to stop
wait

# Cleanup
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
