# 🚀 Trading AI Framework - Full Setup Guide

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

**Python Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### Step 2: Start Backend (Terminal 1)
```bash
python api.py
# Output: 🚀 Starting Trading AI Framework API Server
#         📍 Server running at http://localhost:5000
```

### Step 3: Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
# Output: ➜  Local:   http://localhost:3000/
```

### Step 4: Open Browser
Navigate to: **http://localhost:3000**

---

## Full Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser                           │
│              React TypeScript UI (Port 3000)             │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Dashboard                                       │   │
│  │  ├─ Start/Stop Buttons                          │   │
│  │  ├─ Progress Bar (Real-time Updates)            │   │
│  │  ├─ Algorithm List Display                      │   │
│  │  └─ 4 Charts + Results Table                    │   │
│  └──────────────────────────────────────────────────┘   │
│                        │                                 │
│                        │ HTTP Requests                   │
│                        ▼                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Vite Dev Server (Proxy to :5000)                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                        │
                        │ /api/run-simulation
                        │ /api/simulation-info
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Flask API Server (Port 5000)                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ REST Endpoints                                   │   │
│  │ ├─ GET /health                                 │   │
│  │ ├─ GET /run-simulation                         │   │
│  │ └─ GET /simulation-info                        │   │
│  └──────────────────────────────────────────────────┘   │
│                        │                                 │
│                        ▼                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Python Trading Framework                         │   │
│  │ ├─ BenchmarkRunner                              │   │
│  │ ├─ 6 Trading Algorithms                         │   │
│  │ ├─ State-Space Search Logic                     │   │
│  │ └─ Memory Tracking (tracemalloc)                │   │
│  └──────────────────────────────────────────────────┘   │
│                        │                                 │
│                        ▼                                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Historical Price Data (CSV)                      │   │
│  │ data/sample_prices.csv                          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## File Structure

```
trading_ai_framework/
├── main.py                    # Original CLI entry point
├── evaluation.py              # BenchmarkRunner class
├── state.py                   # Trading state & actions
├── utils.py                   # Utilities (data loading, charts)
├── api.py                     # NEW: Flask backend server
├── requirements.txt           # Python dependencies
│
├── algorithms/                # Trading algorithm implementations
│   ├── base.py
│   ├── bfs.py
│   ├── dfs.py
│   ├── astar.py
│   ├── minimax.py
│   ├── ao_star.py
│   └── buy_and_hold.py
│
├── data/
│   └── sample_prices.csv      # Historical stock prices
│
├── output/                    # Generated charts/reports
│
└── frontend/                  # NEW: React TypeScript UI
    ├── package.json           # Node.js dependencies
    ├── tsconfig.json          # TypeScript config
    ├── vite.config.ts         # Vite build config
    ├── index.html             # HTML entry point
    ├── src/
    │   ├── main.tsx           # React entry point
    │   ├── App.tsx            # Main app component
    │   ├── App.css            # Global styles
    │   └── components/
    │       ├── SimulationControls.tsx
    │       ├── SimulationControls.css
    │       ├── SimulationDashboard.tsx
    │       ├── SimulationDashboard.css
    │       ├── AlgorithmResults.tsx
    │       └── AlgorithmResults.css
    └── README.md
```

---

## Features Breakdown

### 🎮 Simulation Controls
- **Start Button**: Triggers simulation on backend
- **Stop Button**: Halts running simulation
- **Status Indicator**: Shows running/ready state
- **Info Cards**: Displays framework info

### 📊 Real-Time Dashboard
- **Progress Bar**: Animated progress (0-100%)
- **Current Algorithm**: Shows which algorithm is running
- **Algorithm List**: Displays all 6 available strategies
- **Status Message**: "Processing trading strategies..." while running

### 📈 Results Visualization
- **Profit Comparison**: Bar chart of portfolio values
- **Performance Scatter**: Execution time vs. states explored
- **Memory Usage**: Peak memory consumption chart
- **Efficiency Metrics**: Profit per second / profit per state
- **Detailed Table**: Sortable results with all metrics

---

## API Documentation

### 1. Health Check
```bash
curl http://localhost:5000/health
```

**Response (200):**
```json
{
  "status": "healthy",
  "message": "Trading AI Framework API is running",
  "version": "1.0.0"
}
```

### 2. Run Simulation
```bash
curl "http://localhost:5000/run-simulation?cash=10000&minimax_depth=5"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| data | string | data/sample_prices.csv | Price data CSV path |
| cash | number | 10000 | Starting capital ($) |
| minimax_depth | number | 5 | Minimax search depth |
| ao_depth | number | 5 | AO* search depth |

**Response (200):**
```json
{
  "status": "success",
  "results": [
    {
      "name": "A*",
      "final_value": 12500.50,
      "profit": 2500.50,
      "execution_time": 0.1234,
      "states_explored": 450,
      "peak_memory": 512.5
    }
  ],
  "summary": {
    "total_algorithms": 6,
    "total_profit_combined": 15000,
    "average_execution_time": 0.15,
    "best_algorithm": "A*",
    "best_profit": 3000,
    "data_file": "data/sample_prices.csv",
    "starting_capital": 10000,
    "price_data_points": 252
  }
}
```

### 3. Simulation Info
```bash
curl http://localhost:5000/simulation-info
```

**Response (200):**
```json
{
  "algorithms": [
    {
      "name": "Buy & Hold",
      "description": "Baseline strategy - buy and hold throughout",
      "type": "baseline"
    },
    {
      "name": "BFS",
      "description": "Breadth-First Search - explores all options at each level",
      "type": "search"
    }
  ],
  "default_parameters": {
    "starting_cash": 10000,
    "minimax_depth": 5,
    "ao_depth": 5,
    "transaction_fee": 0.001
  },
  "data_files": ["data/sample_prices.csv"]
}
```

---

## Development Workflows

### Add a New Chart
1. Edit `frontend/src/components/AlgorithmResults.tsx`
2. Add import from Recharts
3. Create chart data structure
4. Add `<ChartComponent>` inside `.charts-grid`
5. Style with CSS module

### Customize Dashboard Colors
Edit `frontend/src/App.css` and component CSS files:
```css
/* Purple gradient primary */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Custom algorithm colors */
#667eea (Primary Blue)
#764ba2 (Secondary Purple)
#f093fb (Pink)
#f5576c (Red)
#22c55e (Green)
#f59e0b (Amber)
```

### Change Simulation Parameters
Frontend:
- Edit `frontend/src/App.tsx` → `startSimulation()` function

Backend:
- Edit `api.py` → `/run-simulation` endpoint default values

### Add Real-Time Updates (WebSocket)
Replace polling with WebSocket in `frontend/src/App.tsx`:
```typescript
const socket = new WebSocket('ws://localhost:5000/simulation-updates');
socket.onmessage = (event) => {
  const update = JSON.parse(event.data);
  setSimulationState(prev => ({
    ...prev,
    progress: update.progress,
    currentAlgorithm: update.algorithm
  }));
};
```

---

## Troubleshooting

### ❌ "Cannot GET /api/run-simulation"
**Cause**: Backend not running or proxy misconfigured
**Fix**:
```bash
# Terminal 1: Start backend
python api.py

# Check vite.config.ts has correct proxy:5000
```

### ❌ "CORS error in browser console"
**Cause**: Flask CORS not allowing frontend origin
**Fix** in `api.py`:
```python
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
```

### ❌ "Module 'flask' not found"
**Cause**: Missing dependencies
**Fix**:
```bash
pip install -r requirements.txt
```

### ❌ "Port 5000 already in use"
**Fix**:
```bash
python api.py --port 8000
# Update vite.config.ts proxy target to :8000
```

### ❌ "Simulation returns no results"
**Cause**: data/sample_prices.csv missing or malformed
**Fix**:
- Verify CSV exists in `data/` directory
- Check CSV format: date, price columns

---

## Performance Tips

1. **Increase Simulation Speed**: Reduce minimax/ao_depth in parameters
2. **Optimize Memory**: Chart rendering throttling in results component
3. **Production Build**: `cd frontend && npm run build` creates optimized dist/

---

## Next Steps

### Enhance the UI
- [ ] Add WebSocket for real-time updates
- [ ] Implement simulation progress logging
- [ ] Add configuration panel for parameters
- [ ] Export results to CSV/PDF

### Backend Improvements
- [ ] Add database (PostgreSQL) for result history
- [ ] Implement caching for repeated simulations
- [ ] Add WebSocket for streaming updates
- [ ] Create async job queue for long-running simulations

### Deployment
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] CI/CD pipeline (GitHub Actions)

---

## Resources

- [React Docs](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Recharts Documentation](https://recharts.org/)

---

**Questions?** Check individual README files:
- `frontend/README.md` - UI documentation
- Root `README.md` - Framework documentation

Happy Trading! 🚀📊
