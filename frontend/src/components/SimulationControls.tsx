import React from 'react';
import './SimulationControls.css';

interface SimulationControlsProps {
  isRunning: boolean;
  onStart: () => void;
  onStop: () => void;
}

const SimulationControls: React.FC<SimulationControlsProps> = ({
  isRunning,
  onStart,
  onStop,
}) => {
  return (
    <div className="controls-container">
      <div className="control-group">
        <h2>Simulation Control</h2>
        <div className="button-group">
          <button
            className={`btn btn-start ${isRunning ? 'disabled' : ''}`}
            onClick={onStart}
            disabled={isRunning}
          >
            <span className="btn-icon">▶️</span> Start Simulation
          </button>
          <button
            className={`btn btn-stop ${!isRunning ? 'disabled' : ''}`}
            onClick={onStop}
            disabled={!isRunning}
          >
            <span className="btn-icon">⏹️</span> Stop
          </button>
        </div>
      </div>

      <div className="info-grid">
        <div className="info-card">
          <span className="info-label">Status</span>
          <span className="info-value">
            {isRunning ? (
              <span className="status-running">🟢 Running</span>
            ) : (
              <span className="status-idle">🔵 Ready</span>
            )}
          </span>
        </div>
        <div className="info-card">
          <span className="info-label">Framework</span>
          <span className="info-value">State-Space Search</span>
        </div>
        <div className="info-card">
          <span className="info-label">Algorithms</span>
          <span className="info-value">6 Strategies</span>
        </div>
      </div>
    </div>
  );
};

export default SimulationControls;
