#!/bin/bash
# Development server startup script

echo "Starting Encrypted Messaging API in development mode..."
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment not activated"
    echo "Activate it with: source venv/bin/activate"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found"
    echo "Copy .env.example to .env and configure it"
    exit 1
fi

# Run database initialization
echo "Initializing database..."
python init_db.py

echo ""
echo "Starting server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""

# Start uvicorn server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
