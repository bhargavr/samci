# Quick Start Guide

Get the Granite Crate Packing Optimizer running in 3 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Terminal access

## Option 1: Automated Setup (Recommended)

```bash
# Make script executable (first time only)
chmod +x start.sh

# Run the application
./start.sh
```

This will:
1. Set up Python virtual environment
2. Install backend dependencies
3. Install frontend dependencies
4. Start both servers
5. Open your browser

**URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

Press `Ctrl+C` to stop all services.

## Option 2: Manual Setup

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python api/main.py
```

Backend runs on: http://localhost:8000

### Frontend (New Terminal)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs on: http://localhost:3000

## Test the Backend Directly

```bash
cd backend
source venv/bin/activate
python test_example.py
```

This runs a standalone test without the API server.

## First Steps

1. **Load Example**: Click "Load Example" to fill in sample data
2. **Optimize**: Click "Optimize Packing"
3. **View Results**: Rotate the 3D view (left-click + drag)
4. **Step Mode**: Enable to see placement instructions one by one

## Sample cURL Request

```bash
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "container": {
      "length": 5898,
      "width": 2352,
      "height": 2393,
      "max_weight": 28000
    },
    "crates": [
      {
        "id": "Large-Granite",
        "length": 1200,
        "width": 1000,
        "height": 800,
        "weight": 1200,
        "quantity": 10,
        "max_stack": 2,
        "can_rotate": true
      }
    ],
    "gap_tolerance": 50.0
  }'
```

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is in use: `lsof -i :8000`
- Make sure virtual environment is activated
- Verify Python 3.8+ with `python --version`

**Frontend won't start:**
- Check if port 3000 is in use
- Try deleting `node_modules` and running `npm install` again
- Make sure Node.js 16+ with `node --version`

**CORS errors:**
- Ensure backend is running on http://localhost:8000
- Check browser console for specific errors

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API docs at http://localhost:8000/docs
- Modify crate configurations and experiment!

---

**Need help?** Check the troubleshooting section in README.md
