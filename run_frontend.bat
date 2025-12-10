@echo off
REM Windows batch script to run the frontend

echo.
echo ========================================
echo   Library Desk Agent - Frontend UI
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

echo.
echo Starting Streamlit UI...
echo The app will open in your browser automatically.
echo Press Ctrl+C to stop
echo.

streamlit run app\main.py

