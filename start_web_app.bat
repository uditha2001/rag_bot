@echo off
echo Starting RAG Bot Web Application...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Start backend server
echo 🚀 Starting FastAPI backend server...
start "RAG Bot Backend" cmd /k "D:/aiCourse/Rag-Bot/virtualEnv/Scripts/python.exe web_server.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Check if web_ui directory exists and install dependencies
if not exist "web_ui\node_modules" (
    echo 📦 Installing React dependencies...
    cd web_ui
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install React dependencies
        pause
        exit /b 1
    )
    cd ..
)

REM Start frontend
echo 🎨 Starting React frontend...
cd web_ui
start "RAG Bot Frontend" cmd /k "npm start"
cd ..

echo.
echo ✅ RAG Bot is starting up!
echo.
echo 🌐 Frontend will be available at: http://localhost:3000
echo 🔧 Backend API is available at: http://localhost:8000
echo.
echo Press any key to close this window...
pause >nul
