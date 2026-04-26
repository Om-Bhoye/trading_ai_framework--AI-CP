# Trading AI Framework - TypeScript UI

A modern React TypeScript dashboard for visualizing and controlling trading algorithm simulations in real-time.

## Features

✨ **Real-Time Simulation Dashboard**
- Live progress tracking with animated progress bar
- Current algorithm display with status updates
- Comprehensive visualization of all 6 trading algorithms

📊 **Multi-Layer Data Visualization**
- Portfolio value and profit comparison (bar charts)
- Execution time vs. states explored (scatter plot)
- Memory usage analysis
- Profit efficiency metrics
- Detailed results table with rankings

🎮 **Intuitive Controls**
- One-click simulation start
- Stop/pause functionality
- Status indicators
- Algorithm information cards

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: CSS3 with gradients and animations
- **Charts**: Recharts for data visualization
- **HTTP Client**: Axios
- **Backend Integration**: REST API with Flask

## Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+

### Setup

1. **Install Frontend Dependencies**
```bash
cd frontend
npm install
```

2. **Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

## Running the Application

### Terminal 1: Start Backend API
```bash
python api.py
```
Backend runs on `http://localhost:5000`

### Terminal 2: Start Frontend Dev Server
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3000`

### Open in Browser
Navigate to `http://localhost:3000`

## Usage

1. **Click "Start Simulation"** button to begin
2. Watch the progress bar as algorithms run
3. View results including:
   - Portfolio values and profits
   - Execution times and state counts
   - Memory usage
   - Efficiency metrics
4. Compare algorithms side-by-side in charts and tables

## Component Architecture

```
src/
├── App.tsx                    # Main application component
├── components/
│   ├── SimulationControls.tsx # Control buttons and info cards
│   ├── SimulationDashboard.tsx # Progress display & algorithm list
│   └── AlgorithmResults.tsx    # Charts, table, and metrics
├── App.css                    # Main styles
└── main.tsx                   # React entry point
```

## API Endpoints

### GET `/health`
Health check endpoint

### GET `/run-simulation`
Run all trading algorithms

**Query Parameters:**
- `data` (string): Path to price data CSV (default: `data/sample_prices.csv`)
- `cash` (number): Starting capital (default: `10000`)
- `minimax_depth` (number): Minimax search depth (default: `5`)
- `ao_depth` (number): AO* search depth (default: `5`)

**Response:**
```json
{
  "status": "success",
  "results": [
    {
      "name": "Algorithm Name",
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
    "best_profit": 3000
  }
}
```

### GET `/simulation-info`
Get information about available algorithms and configurations

## Building for Production

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/` directory

## Environment Variables

No environment variables required for basic setup. For production:
- Set `BACKEND_URL` to your Flask server URL
- Configure CORS settings in `api.py`

## Performance Monitoring

The dashboard displays:
- **Execution Time**: How long each algorithm took to run
- **States Explored**: Complexity proxy (lower is better)
- **Memory Usage**: Peak memory consumption
- **Profit Efficiency**: Profit per second and per state explored

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

**Frontend won't connect to backend?**
- Ensure Flask API is running on port 5000
- Check CORS settings in `api.py`
- Verify proxy configuration in `vite.config.ts`

**Simulation fails with "File not found"?**
- Verify `data/sample_prices.csv` exists
- Check file path in API request

**Charts not displaying?**
- Clear browser cache
- Rebuild frontend: `npm run build`

## License

MIT - See LICENSE file in root directory

## Author

Trading AI Framework Team

---

**Need help?** Check the main README.md in the root directory for full framework documentation.
