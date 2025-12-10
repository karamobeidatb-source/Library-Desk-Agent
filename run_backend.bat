@echo off
REM Windows batch script to run the backend server

echo.
echo ========================================
echo   Library Desk Agent - Backend Server
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found at venv\
    echo Running with system Python...
)

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ERROR: .env file not found!
    echo Please copy env.example to .env and add your OpenAI API key.
    echo.
    pause
    exit /b 1
)

REM Check if database exists
if not exist "db\library.db" (
    echo.
    echo Database not found. Initializing...
    python db\init_db.py
    echo.
)

echo Starting backend server...
echo Server will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop
echo.

python server\main.py

