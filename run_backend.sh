#!/bin/bash
# Unix/Linux/macOS script to run the backend server

echo ""
echo "========================================"
echo "  Library Desk Agent - Backend Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Warning: Virtual environment not found at venv/"
    echo "Running with system Python..."
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "ERROR: .env file not found!"
    echo "Please copy env.example to .env and add your OpenAI API key."
    echo ""
    exit 1
fi

# Check if database exists
if [ ! -f "db/library.db" ]; then
    echo ""
    echo "Database not found. Initializing..."
    python db/init_db.py
    echo ""
fi

echo "Starting backend server..."
echo "Server will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop"
echo ""

python server/main.py

