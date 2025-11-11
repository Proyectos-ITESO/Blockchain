#!/bin/bash
# Complete startup script for development

set -e

echo "🚀 Starting Encrypted Messaging System"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/fastapi/__init__.py" ]; then
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Copy .env.example to .env and configure it"
    echo "  cp .env.example .env"
    exit 1
fi

# Initialize database if needed
echo -e "${GREEN}Initializing database...${NC}"
python init_db.py || true

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
echo "Backend will be available at: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

# Check if frontend should be started
if [ -d "frontend" ]; then
    echo -e "${YELLOW}To start frontend, open a new terminal and run:${NC}"
    echo "  cd frontend"
    echo "  npm install"
    echo "  npm run dev"
    echo ""
fi

# Start uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
