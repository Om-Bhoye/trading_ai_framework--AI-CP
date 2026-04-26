import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SimulationDashboard from './components/SimulationDashboard';
import SimulationControls from './components/SimulationControls';
import AlgorithmResults from './components/AlgorithmResults';
import './App.css';

interface SimulationState {
  isRunning: boolean;
  progress: number;
  currentAlgorithm: string;
  results: any[];
  error: string | null;
}

function App() {
  const [simulationState, setSimulationState] = useState<SimulationState>({
    isRunning: false,
    progress: 0,
    currentAlgorithm: '',
    results: [],
    error: null,
  });

  const startSimulation = async () => {
    setSimulationState({
      isRunning: true,
      progress: 0,
      currentAlgorithm: 'Initializing...',
      results: [],
      error: null,
    });

    try {
      const response = await axios.get('/api/run-simulation', {
        params: {
          data: 'data/sample_prices.csv',
          cash: 10000,
        }
      });

      setSimulationState({
        isRunning: false,
        progress: 100,
        currentAlgorithm: 'Completed',
        results: response.data.results || [],
        error: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setSimulationState(prev => ({
        ...prev,
        isRunning: false,
        error: errorMessage,
      }));
    }
  };

  const stopSimulation = () => {
    setSimulationState(prev => ({
      ...prev,
      isRunning: false,
    }));
  };

  useEffect(() => {
    if (simulationState.isRunning) {
      const progressInterval = setInterval(() => {
        setSimulationState(prev => ({
          ...prev,
          progress: Math.min(prev.progress + Math.random() * 15, 95),
        }));
      }, 800);

      return () => clearInterval(progressInterval);
    }
  }, [simulationState.isRunning]);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚀 Trading AI Framework - Simulation Dashboard</h1>
        <p>Compare multiple trading algorithms in real-time</p>
      </header>

      <main className="app-main">
        <div className="controls-section">
          <SimulationControls
            isRunning={simulationState.isRunning}
            onStart={startSimulation}
            onStop={stopSimulation}
          />
        </div>

        {simulationState.error && (
          <div className="error-banner">
            ⚠️ Error: {simulationState.error}
          </div>
        )}

        <SimulationDashboard
          isRunning={simulationState.isRunning}
          progress={simulationState.progress}
          currentAlgorithm={simulationState.currentAlgorithm}
        />

        {simulationState.results.length > 0 && (
          <AlgorithmResults results={simulationState.results} />
        )}
      </main>

      <footer className="app-footer">
        <p>© 2024 Trading AI Framework | State-Space Search Optimization</p>
      </footer>
    </div>
  );
}

export default App;
