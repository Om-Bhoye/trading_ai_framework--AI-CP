import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
} from 'recharts';
import './AlgorithmResults.css';

interface AlgorithmResult {
  name: string;
  final_value: number;
  execution_time: number;
  states_explored: number;
  peak_memory: number;
  profit: number;
  actions: string[];
}

interface AlgorithmResultsProps {
  results: AlgorithmResult[];
}

const AlgorithmResults: React.FC<AlgorithmResultsProps> = ({ results }) => {
  // Prepare data for charts
  const profitData = results.map(r => ({
    name: r.name,
    profit: r.profit,
    final_value: r.final_value,
  }));

  const performanceData = results.map(r => ({
    name: r.name,
    time: r.execution_time,
    states: r.states_explored,
    memory: r.peak_memory,
  }));

  const efficiencyData = results.map(r => ({
    name: r.name,
    profitPerSecond: r.final_value / (r.execution_time || 1),
    profitPerState: r.final_value / (r.states_explored || 1),
  }));

  const getBestAlgorithm = () => {
    return results.reduce((best, current) => {
      if (current.profit > best.profit) return current;
      if (current.profit === best.profit && current.execution_time < best.execution_time) return current;
      return best;
    });
  };

  const bestAlgo = getBestAlgorithm();

  return (
    <div className="results-section">
      <h2>📊 Simulation Results</h2>

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="card best-performer">
          <div className="card-label">🏆 Best Performer</div>
          <div className="card-value">{bestAlgo.name}</div>
          <div className="card-detail">Profit: ${bestAlgo.profit.toFixed(2)}</div>
        </div>
        <div className="card algorithms-run">
          <div className="card-label">🔄 Algorithms Tested</div>
          <div className="card-value">{results.length}</div>
          <div className="card-detail">All strategies evaluated</div>
        </div>
        <div className="card avg-time">
          <div className="card-label">⏱️ Avg. Execution Time</div>
          <div className="card-value">
            {(
              results.reduce((sum, r) => sum + r.execution_time, 0) /
              results.length
            ).toFixed(3)}
            s
          </div>
          <div className="card-detail">Average across all</div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-grid">
        {/* Profit Chart */}
        <div className="chart-container">
          <h3>Final Portfolio Value vs Profit</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={profitData}
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={value => `$${Number(value).toFixed(2)}`} />
              <Legend />
              <Bar dataKey="final_value" fill="#94a3b8" name="Final Value" />
              <Bar dataKey="profit" fill="#3b82f6" name="Profit" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Performance Metrics */}
        <div className="chart-container">
          <h3>Execution Time vs States Explored</h3>
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                dataKey="time"
                name="Execution Time (s)"
              />
              <YAxis type="number" dataKey="states" name="States Explored" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter
                name="Algorithm Performance"
                data={performanceData}
                fill="#3b82f6"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        {/* Memory Usage */}
        <div className="chart-container">
          <h3>Peak Memory Usage</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={performanceData}
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={value => `${Number(value).toFixed(2)} KB`} />
              <Bar dataKey="memory" fill="#64748b" name="Memory (KB)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Efficiency Metrics */}
        <div className="chart-container">
          <h3>Profit Efficiency</h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart
              data={efficiencyData}
              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip formatter={value => `$${Number(value).toFixed(2)}`} />
              <Legend />
              <Bar
                dataKey="profitPerSecond"
                fill="#10b981"
                name="Profit/Second"
              />
              <Bar
                dataKey="profitPerState"
                fill="#6366f1"
                name="Profit/State"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Results Table */}
      <div className="results-table-container">
        <h3>Detailed Results</h3>
        <table className="results-table">
          <thead>
            <tr>
              <th>Algorithm</th>
              <th>Final Value</th>
              <th>Profit</th>
              <th>Time (s)</th>
              <th>States</th>
              <th>Memory (KB)</th>
              <th>Strategy Sequence</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr
                key={index}
                className={result.name === bestAlgo.name ? 'best-row' : ''}
              >
                <td className="algo-name">{result.name}</td>
                <td className="value">${result.final_value.toFixed(2)}</td>
                <td className="value">${result.profit.toFixed(2)}</td>
                <td className="value">{result.execution_time.toFixed(4)}</td>
                <td className="value">{result.states_explored}</td>
                <td className="value">{result.peak_memory.toFixed(2)}</td>
                <td className="actions-cell">
                  <div className="actions-list">
                    {result.actions && result.actions.length > 0 ? (
                      result.actions.map((action, i) => (
                        <span key={i} className={`action-badge ${action.toLowerCase()}`}>
                          {action[0]}
                        </span>
                      ))
                    ) : (
                      <span className="no-actions">-</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AlgorithmResults;
