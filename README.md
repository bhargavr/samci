# Granite Crate Container Packing Optimizer

A full-stack application for optimizing the placement of granite crates in shipping containers. Maximizes space utilization while ensuring stability, respecting stacking limits, and maintaining real-world logistics constraints.

## Features

- **Custom Heuristic Packing Algorithm**: Implements floor packing with intelligent stacking logic
- **3D Visualization**: Interactive Three.js viewer with rotate, pan, and zoom controls
- **Step-by-Step Mode**: View placement instructions one crate at a time
- **Real-World Constraints**:
  - No overhang (crates must fully sit on base)
  - Max stack height per crate type
  - Weight limits and distribution
  - Gap tolerance for practical fitting
- **Metrics Dashboard**: Space utilization, weight distribution, warnings
- **AWS Serverless Deployment**: Complete cloud infrastructure with auto-scaling and $2-5/month cost

## Architecture

```
samci/
├── backend/              # Python FastAPI service
│   ├── packing/          # Core packing algorithm
│   │   ├── models.py     # Data models
│   │   ├── packer.py     # Heuristic algorithm
│   │   ├── constraints.py # Validation logic
│   │   └── utils.py      # Utilities
│   └── api/
│       └── main.py       # FastAPI endpoints
└── frontend/             # React + Three.js UI
    └── src/
        ├── components/   # UI components
        └── App.jsx       # Main application
```

## Algorithm Overview

### Step 1: Expand Crates
Convert crate types with quantities into individual instances.

### Step 2: Sort Crates
- Sort by footprint (length × width) descending
- Then by weight (heaviest first)
- This ensures large, heavy crates are placed first

### Step 3: Floor Packing
- Use free space tracking (guillotine cuts)
- Place crates row-by-row on container floor
- Try both orientations if rotation allowed

### Step 4: Stacking Logic
- Only stack if:
  - Top crate footprint ≤ bottom crate footprint (no overhang)
  - Stack count ≤ max_stack for base crate
  - Total height ≤ container height
- Maintain stack tower tracking

### Step 5: Constraint Validation
- Check weight limits and distribution
- Validate no overlaps or out-of-bounds
- Generate warnings for stability issues

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Installation & Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend Server

```bash
cd backend

# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run FastAPI server
python api/main.py
```

The API will be available at: `http://localhost:8000`

API documentation (Swagger): `http://localhost:8000/docs`

### Start Frontend Development Server

```bash
cd frontend

# Run Vite dev server
npm run dev
```

The application will open at: `http://localhost:3000`

## ☁️ AWS Deployment

Deploy to AWS with a fully serverless architecture (Lambda + API Gateway + S3 + CloudFront).

### Quick Start

```bash
# 1. Install AWS CLI and SAM CLI (see AWS_DEPLOYMENT.md)

# 2. Configure AWS credentials
aws configure

# 3. Deploy backend (Lambda + API Gateway)
./deploy-backend.sh

# 4. Deploy frontend (S3 + CloudFront)
./deploy-frontend.sh
```

**Cost:** $2-5/month for MVP usage (10K requests/month)

**Documentation:**
- **[AWS_QUICK_START.md](AWS_QUICK_START.md)** - Deploy in 10 minutes
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - Complete deployment guide
- **[AWS_SUMMARY.md](AWS_SUMMARY.md)** - Architecture overview
- **[CI_CD_SETUP.md](CI_CD_SETUP.md)** - Automated pipelines
- **[COST_OPTIMIZATION.md](COST_OPTIMIZATION.md)** - Reduce AWS costs

**Features:**
- ✅ Auto-scaling (1 to 1M requests)
- ✅ Global CDN (CloudFront)
- ✅ HTTPS by default
- ✅ Pay-per-use ($0 when idle)
- ✅ Automated CI/CD (GitHub Actions + GitLab CI)

## Usage

### 1. Configure Container
- Enter container dimensions (mm)
- Set maximum weight capacity (kg)

### 2. Add Crate Types
- Define crate dimensions (length, width, height in mm)
- Set weight per crate (kg)
- Specify quantity
- Set max stack height (1-10)
- Toggle rotation option

### 3. Optimize
- Click "Optimize Packing"
- View results in 3D visualization
- Check utilization metrics
- Review warnings if any

### 4. Step-by-Step Mode
- Enable step mode to see placement instructions
- Navigate through each step
- Watch crates being placed one by one

## Example Input

```json
{
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
    },
    {
      "id": "Medium-Granite",
      "length": 1000,
      "width": 800,
      "height": 700,
      "weight": 900,
      "quantity": 20,
      "max_stack": 3,
      "can_rotate": true
    }
  ],
  "gap_tolerance": 50.0
}
```

## API Endpoints

### `POST /optimize`
Optimize crate packing.

**Request Body:**
```json
{
  "container": { ... },
  "crates": [ ... ],
  "gap_tolerance": 50.0
}
```

**Response:**
```json
{
  "utilization_percent": 91.2,
  "weight_utilization": 88.5,
  "total_crates_packed": 28,
  "total_weight": 24600,
  "placements": [ ... ],
  "unpacked_crates": [ ... ],
  "weight_distribution": { ... },
  "warnings": [ ... ],
  "steps": [ ... ]
}
```

### `GET /examples/standard-container`
Get example input for a standard 20ft container.

### `GET /`
Health check endpoint.

## Key Design Decisions

### Why Custom Algorithm vs. Library?
- Full control over packing logic
- Transparent, explainable results
- Easy to add domain-specific constraints
- No black-box behavior

### Why Heuristic vs. Optimization Solver?
- Fast execution (sub-second for typical loads)
- Good-enough solutions for practical use
- No complex dependencies
- Easy to understand and modify

### Constraint Hierarchy
1. **Hard Constraints** (must satisfy):
   - Container boundaries
   - Weight limits
   - No overhang
   - Max stack heights

2. **Soft Constraints** (optimize for):
   - Weight distribution
   - Space utilization
   - Stability

## Limitations

- Algorithm is heuristic (not guaranteed optimal)
- Does not account for:
  - Center of gravity calculations
  - Dynamic loading during transport
  - Door access constraints
  - Unloading order
- No support for non-rectangular shapes

## Future Enhancements

- Export packing plan as PDF
- Top-view 2D layout diagram
- Weight heatmap visualization
- Save/load configurations
- Multiple container comparison
- Loading sequence optimization
- Cost calculations (shipping rates)

## Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
```

**Module import errors:**
```bash
# Make sure you're in the backend directory with venv activated
cd backend
source venv/bin/activate
python api/main.py
```

### Frontend Issues

**Port 3000 already in use:**
Edit `frontend/vite.config.js` and change the port.

**Dependencies not installing:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
Make sure backend is running on `http://localhost:8000`.

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- Pydantic - Data validation
- Uvicorn - ASGI server

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Three.js - 3D rendering
- @react-three/fiber - React renderer for Three.js
- @react-three/drei - Helper components

## License

MIT

## Contributing

Contributions welcome! Areas for improvement:
- Algorithm optimizations
- Additional visualization modes
- Export formats
- Mobile responsiveness
- Performance profiling

---

Built with focus on explainability, usability, and real-world logistics constraints.
