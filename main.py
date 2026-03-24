"""
main.py — Entry Point for the Trading AI Framework
====================================================

State-Space Search-Based Framework for Trading Strategy
Optimization and Benchmarking.

This script:
    1. Loads historical stock price data from a CSV file.
    2. Runs all six algorithms (Buy & Hold, BFS, DFS, A*, Minimax, AO*)
       via the BenchmarkRunner.
    3. Prints a formatted ASCII comparison table (with memory metrics).
    4. Generates publication-quality charts (bar + scatter).

Usage:
    python main.py                          # Uses default sample data
    python main.py --data path/to/data.csv  # Custom dataset
    python main.py --cash 5000              # Custom starting capital

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from utils import load_price_data, print_results_table, generate_charts
from evaluation import BenchmarkRunner
from algorithms.base import SearchResult


# ---------------------------------------------------------------------------
# CLI Argument Parser
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Namespace with `data`, `cash`, `minimax_depth`, `ao_depth`.
    """
    parser = argparse.ArgumentParser(
        description=(
            "State-Space Search-Based Framework for Trading Strategy "
            "Optimization and Benchmarking"
        ),
    )
    parser.add_argument(
        "--data",
        type=str,
        default=os.path.join("data", "sample_prices.csv"),
        help="Path to the CSV file with columns [Day, Price].",
    )
    parser.add_argument(
        "--cash",
        type=float,
        default=1000.0,
        help="Initial cash balance (default: $1,000).",
    )
    parser.add_argument(
        "--minimax-depth",
        type=int,
        default=6,
        help="Depth limit for Minimax search (default: 6).",
    )
    parser.add_argument(
        "--ao-depth",
        type=int,
        default=6,
        help="Depth limit for AO* search (default: 6).",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Orchestrate the full benchmark pipeline:
        Load data → Run algorithms → Print table → Generate charts.
    """
    args = parse_args()

    # ---- Banner ------------------------------------------------------------
    print()
    print("=" * 65)
    print("  STATE-SPACE SEARCH FRAMEWORK")
    print("  Trading Strategy Optimization & Benchmarking")
    print("=" * 65)
    print()

    # ---- Step 1: Load data -------------------------------------------------
    print("[1/3] Loading price data ...")
    try:
        prices: List[float] = load_price_data(args.data)
    except (FileNotFoundError, KeyError) as e:
        print(f"  [ERR] Error: {e}")
        sys.exit(1)

    print(f"       Prices : {prices[:10]}{'...' if len(prices) > 10 else ''}")
    print(f"       Days   : {len(prices)}")
    print(f"       Cash   : ${args.cash:,.2f}")
    print()

    # ---- Step 2: Run benchmark ---------------------------------------------
    print("[2/3] Running search algorithms ...")
    runner = BenchmarkRunner(
        prices=prices,
        initial_cash=args.cash,
        minimax_depth=args.minimax_depth,
        ao_star_depth=args.ao_depth,
    )
    results: List[SearchResult] = runner.run_all()
    print()

    # ---- Step 3: Results & Visualisation -----------------------------------
    print("[3/3] Results & Visualisation")
    print_results_table(results)

    # Generate charts in the project directory.
    charts_dir: str = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(charts_dir, exist_ok=True)
    generate_charts(results, output_dir=charts_dir)

    print()
    print("=" * 65)
    print("  Benchmark complete.  Charts saved to ./output/")
    print("=" * 65)
    print()


if __name__ == "__main__":
    main()
