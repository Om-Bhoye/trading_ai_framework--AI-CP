"""
api.py — Flask Backend for Trading AI Framework UI
====================================================

Provides REST API endpoints for the TypeScript frontend to:
1. Trigger simulations
2. Stream progress updates
3. Return formatted results

Usage:
    python api.py                       # Runs on http://localhost:5000
    python api.py --port 8000          # Custom port

Author: Framework Team
License: MIT
"""

from __future__ import annotations

import argparse
import json
from typing import Dict, Any
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import load_price_data, print_results_table, generate_charts
from evaluation import BenchmarkRunner
from algorithms.base import SearchResult

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests


# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns:
        JSON with status and message.
    """
    return jsonify({
        'status': 'healthy',
        'message': 'Trading AI Framework API is running',
        'version': '1.0.0'
    })


# ---------------------------------------------------------------------------
# Main Simulation Endpoint
# ---------------------------------------------------------------------------

@app.route('/run-simulation', methods=['GET', 'POST'])
def run_simulation():
    """
    Run the trading simulation with all algorithms.

    Query Parameters:
        - data (str): Path to CSV data file (default: 'data/sample_prices.csv')
        - cash (float): Starting capital (default: 10000)
        - minimax_depth (int): Minimax search depth (default: 5)
        - ao_depth (int): AO* search depth (default: 5)

    Returns:
        JSON with:
            - status: 'success' or 'error'
            - results: List of algorithm results
            - summary: Overall statistics
    """
    try:
        # Parse parameters
        data_file = request.args.get('data', 'data/sample_prices.csv')
        starting_cash = float(request.args.get('cash', 10000))
        minimax_depth = int(request.args.get('minimax_depth', 5))
        ao_depth = int(request.args.get('ao_depth', 5))

        # Load price data
        prices = load_price_data(data_file)
        if not prices:
            return jsonify({
                'status': 'error',
                'message': f'Failed to load data from {data_file}'
            }), 400

        # Run benchmarks
        runner = BenchmarkRunner(
            prices=prices,
            initial_cash=starting_cash,
            minimax_depth=minimax_depth,
            ao_star_depth=ao_depth
        )

        results = runner.run_all()

        # Format results for frontend
        formatted_results = [
            {
                'name': result.algorithm_name,
                'final_value': result.final_value,
                'profit': result.final_value - starting_cash,
                'execution_time': result.execution_time_s,
                'states_explored': result.states_explored,
                'peak_memory': result.peak_memory_kb,
                'actions': [a.value for a in result.best_actions],
            }
            for result in results
        ]

        # Calculate summary statistics
        total_profit = sum(r['profit'] for r in formatted_results)
        avg_time = sum(r['execution_time'] for r in formatted_results) / len(formatted_results)
        # Tie-breaker: If profits are equal, pick the one with the fastest execution time
        best_algo = max(formatted_results, key=lambda x: (x['profit'], -x['execution_time']))

        summary = {
            'total_algorithms': len(formatted_results),
            'total_profit_combined': total_profit,
            'average_execution_time': avg_time,
            'best_algorithm': best_algo['name'],
            'best_profit': best_algo['profit'],
            'data_file': data_file,
            'starting_capital': starting_cash,
            'price_data_points': len(prices),
        }

        return jsonify({
            'status': 'success',
            'results': formatted_results,
            'summary': summary,
        })

    except FileNotFoundError as e:
        return jsonify({
            'status': 'error',
            'message': f'File not found: {str(e)}'
        }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Simulation failed: {str(e)}'
        }), 500


# ---------------------------------------------------------------------------
# Simulation Info Endpoint
# ---------------------------------------------------------------------------

@app.route('/simulation-info', methods=['GET'])
def simulation_info():
    """
    Get information about available simulations and configurations.

    Returns:
        JSON with available algorithms, parameters, and defaults.
    """
    return jsonify({
        'algorithms': [
            {
                'name': 'Buy & Hold',
                'description': 'Baseline strategy - buy and hold throughout',
                'type': 'baseline'
            },
            {
                'name': 'BFS',
                'description': 'Breadth-First Search - explores all options at each level',
                'type': 'search'
            },
            {
                'name': 'DFS',
                'description': 'Depth-First Search - explores deep paths first',
                'type': 'search'
            },
            {
                'name': 'A*',
                'description': 'A* Search - heuristic-guided optimal search',
                'type': 'search'
            },
            {
                'name': 'Minimax',
                'description': 'Minimax - game theory approach to trading',
                'type': 'adversarial'
            },
            {
                'name': 'AO*',
                'description': 'AO* Search - AND/OR graph search for optimal policies',
                'type': 'search'
            }
        ],
        'default_parameters': {
            'starting_cash': 10000,
            'minimax_depth': 5,
            'ao_depth': 5,
            'transaction_fee': 0.001
        },
        'data_files': [
            'data/sample_prices.csv'
        ]
    })


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'status': 'error', 'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Trading AI Framework API Server'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the Flask server on (default: 5000)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='localhost',
        help='Host to bind to (default: localhost)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )

    args = parser.parse_args()

    print(f'[*] Starting Trading AI Framework API Server')
    print(f'[>] Server running at http://{args.host}:{args.port}')
    print(f'[>] Frontend: http://localhost:3000')
    print(f'[>] Health check: http://{args.host}:{args.port}/health')

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
