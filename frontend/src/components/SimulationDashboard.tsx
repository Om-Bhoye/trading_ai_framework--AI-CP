import React from 'react';
import './SimulationDashboard.css';

interface SimulationDashboardProps {
  isRunning: boolean;
  progress: number;
  currentAlgorithm: string;
}

const SimulationDashboard: React.FC<SimulationDashboardProps> = ({
  isRunning,
  progress,
  currentAlgorithm,
}) => {
  return (
    <div className="dashboard">
      <div className="dashboard-card">
        <h2>Simulation Progress</h2>
        
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <span className="progress-text">{Math.round(progress)}%</span>
        </div>

        <div className="algorithm-info">
          <h3>Current Algorithm</h3>
          <div className="algorithm-display">
            {isRunning ? (
              <>
                <span className="algorithm-spinner">⚙️</span>
                <span className="algorithm-name">{currentAlgorithm}</span>
              </>
            ) : (
              <>
                <span className="algorithm-icon">📊</span>
                <span className="algorithm-name">Ready to start</span>
              </>
            )}
          </div>
        </div>

        <div className="algorithms-list">
          <h3>Available Algorithms</h3>
          <ul>
            <li>
              <span className="algo-icon">📈</span> Buy & Hold (Baseline)
            </li>
            <li>
              <span className="algo-icon">🔍</span> Breadth-First Search (BFS)
            </li>
            <li>
              <span className="algo-icon">🔍</span> Depth-First Search (DFS)
            </li>
            <li>
              <span className="algo-icon">⭐</span> A* Search
            </li>
            <li>
              <span className="algo-icon">🎮</span> Minimax
            </li>
            <li>
              <span className="algo-icon">🌟</span> AO* Search
            </li>
          </ul>
        </div>

        {isRunning && (
          <div className="status-message">
            <span className="spinner"></span>
            Processing trading strategies...
          </div>
        )}
      </div>
    </div>
  );
};

export default SimulationDashboard;
