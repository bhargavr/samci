# Quick Reference Card

## 🚀 Start Application

```bash
./start.sh
```

**URLs:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
samci/
├── backend/          # Python FastAPI service
│   ├── packing/      # Core algorithm
│   └── api/          # REST API
└── frontend/         # React + Three.js UI
    └── src/
        └── components/
```

## 🔧 Commands

### Backend

```bash
cd backend
source venv/bin/activate        # Activate venv
python api/main.py              # Start server
python test_example.py          # Run tests
```

### Frontend

```bash
cd frontend
npm install                     # Install deps
npm run dev                     # Start dev server
npm run build                   # Production build
```

## 🎯 API Quick Test

```bash
# Health check
curl http://localhost:8000/

# Optimize
curl -X POST http://localhost:8000/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "container": {
      "length": 5898,
      "width": 2352,
      "height": 2393,
      "max_weight": 28000
    },
    "crates": [{
      "id": "TestCrate",
      "length": 1200,
      "width": 1000,
      "height": 800,
      "weight": 1200,
      "quantity": 10,
      "max_stack": 2,
      "can_rotate": true
    }]
  }'
```

## 🎨 UI Controls

### 3D Viewer
- **Rotate:** Left-click + drag
- **Pan:** Right-click + drag
- **Zoom:** Scroll wheel

### Form
- **Load Example:** Top-right button
- **Add Crate:** Green button
- **Remove Crate:** Red [×] button
- **Optimize:** Purple button at bottom

## 📊 Key Metrics

| Metric | Good | OK | Poor |
|--------|------|-----|------|
| Space Utilization | >80% | 60-80% | <60% |
| Weight Utilization | >85% | 70-85% | <70% |
| Weight Balance | <15% diff | 15-25% | >25% |

## 🔍 Troubleshooting

### Backend won't start
```bash
# Check port
lsof -i :8000

# Kill if needed
lsof -ti:8000 | xargs kill -9

# Reinstall deps
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check port
lsof -i :3000

# Reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS errors
- Ensure backend runs on port 8000
- Check browser console
- Verify fetch URL in frontend

### 3D not rendering
- Check WebGL support
- Open browser console
- Verify three.js installed

## 📝 File Locations

| What | Where |
|------|-------|
| Algorithm | `backend/packing/packer.py` |
| API endpoints | `backend/api/main.py` |
| 3D viewer | `frontend/src/components/Viewer3D.jsx` |
| Input form | `frontend/src/components/InputForm.jsx` |
| Tests | `backend/test_example.py` |

## 🎓 Algorithm Logic

1. **Expand** crates (quantity → instances)
2. **Sort** by footprint descending
3. **Place** on floor (fill rows)
4. **Stack** on existing crates
5. **Validate** constraints
6. **Report** results + warnings

## ⚙️ Configuration

### Container
- Length, width, height (mm)
- Max weight (kg)

### Crate
- Dimensions L×W×H (mm)
- Weight (kg)
- Quantity (count)
- Max stack height (1-10)
- Rotation allowed (bool)

### Settings
- Gap tolerance (mm, default 50)

## 📤 Response Structure

```json
{
  "utilization_percent": 91.2,
  "weight_utilization": 88.5,
  "total_crates_packed": 28,
  "total_weight": 24650,
  "placements": [...],
  "unpacked_crates": [...],
  "weight_distribution": {...},
  "warnings": [...],
  "steps": [...]
}
```

## 🔗 Dependencies

### Backend
- fastapi==0.115.0
- uvicorn==0.32.0
- pydantic==2.9.0

### Frontend
- react ^18.3.1
- @react-three/fiber ^8.17.10
- @react-three/drei ^9.114.3
- three ^0.169.0

## 💡 Tips

1. **Load Example** first to see sample data
2. Start with **few crates** to test
3. Enable **step mode** to understand packing
4. Check **warnings** for issues
5. Adjust **gap tolerance** if tight fit needed
6. **Rotate** container view for better perspective
7. Compare **weight distribution** balance

## 📚 Documentation

- `README.md` - Full guide
- `QUICKSTART.md` - Setup (3 min)
- `FEATURES.md` - Feature list
- `SUMMARY.md` - Project overview
- `VERIFICATION.md` - Testing guide

## 🐛 Known Limitations

- Heuristic (not optimal)
- Rectangular crates only
- No load sequence
- Simple weight model
- No center of gravity

## 🎯 Success Criteria

✅ Packs 20+ crates in 20ft container
✅ >80% space utilization
✅ No constraint violations
✅ <1 second optimization
✅ Smooth 3D rendering

---

**Quick Start:** `./start.sh` → Open http://localhost:3000 → Click "Load Example" → Click "Optimize"
