#!/bin/bash

# Granite Crate Packing Optimizer - Quick Start Script

echo "=========================================="
echo "Granite Crate Packing Optimizer"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Setting up backend virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}Backend setup complete!${NC}"
else
    echo -e "${GREEN}Backend virtual environment found.${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}Frontend setup complete!${NC}"
else
    echo -e "${GREEN}Frontend dependencies found.${NC}"
fi

echo ""
echo "=========================================="
echo "Starting services..."
echo "=========================================="

# Start backend in background
echo -e "${YELLOW}Starting backend server on port 8000...${NC}"
cd backend
source venv/bin/activate
python api/main.py &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
sleep 3

# Start frontend in background
echo -e "${YELLOW}Starting frontend server on port 3000...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Application is running!${NC}"
echo "=========================================="
echo ""
echo "Backend API: http://localhost:8000"
echo "API Docs:    http://localhost:8000/docs"
echo "Frontend:    http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for processes
wait
