#!/bin/bash
# Unix/Linux/macOS script to run the frontend

echo ""
echo "========================================"
echo "  Library Desk Agent - Frontend UI"
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

echo ""
echo "Starting Streamlit UI..."
echo "The app will open in your browser automatically."
echo "Press Ctrl+C to stop"
echo ""

streamlit run app/main.py

