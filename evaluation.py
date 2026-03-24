"""
evaluation.py — Benchmarking Engine & Metric Tracking
======================================================

This module provides the `BenchmarkRunner`, which executes every search
algorithm on the same historical dataset and collects standardised
performance metrics for side-by-side comparison.

Tracked Metrics per Algorithm:
    1. Final Portfolio Value (Profit)
    2. Execution Time (seconds)
    3. Number of States Explored (space-complexity proxy)
    4. Peak Memory Usage (KB) via tracemalloc
    5. Optimal Action Sequence

Memory Tracking:
    Python's built-in `tracemalloc` module is used to capture the peak
    memory allocated during each algorithm's `.search()` call.  This
    provides a concrete, measurable proxy for **space complexity**
    beyond just the state count.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import tracemalloc
from typing import List

from state import Action
from algorithms.base import SearchAlgorithm, SearchResult
from algorithms.bfs import BFSSearch
from algorithms.dfs import DFSSearch
from algorithms.astar import AStarSearch
from algorithms.minimax import MinimaxSearch
from algorithms.ao_star import AOStarSearch
from algorithms.buy_and_hold import BuyAndHoldBaseline


# ---------------------------------------------------------------------------
# Benchmark Runner
# ---------------------------------------------------------------------------

class BenchmarkRunner:
    """
    Orchestrates the execution of all search algorithms on a shared
    price dataset and collects results for comparison.

    Memory Tracking Implementation:
        For each algorithm run we:
            1. Start tracemalloc (or clear its stats).
            2. Execute algorithm.search().
            3. Read tracemalloc.get_traced_memory() to capture peak.
            4. Stop tracemalloc and store the peak in the SearchResult.

    Usage:
        runner = BenchmarkRunner(prices, initial_cash=1000.0)
        results = runner.run_all()

    Each result is a `SearchResult` dataclass with all metrics populated.
    """

    def __init__(
        self,
        prices: List[float],
        initial_cash: float = 1000.0,
        minimax_depth: int = 6,
        ao_star_depth: int = 6,
    ) -> None:
        """
        Initialise the benchmark runner.

        Args:
            prices         : Historical daily stock prices.
            initial_cash   : Starting cash for every algorithm.
            minimax_depth  : Depth limit for Minimax / Alpha-Beta.
            ao_star_depth  : Depth limit for AO* search.
        """
        self.prices: List[float] = prices
        self.initial_cash: float = initial_cash
        self.minimax_depth: int = minimax_depth
        self.ao_star_depth: int = ao_star_depth

    def _build_algorithms(self) -> List[SearchAlgorithm]:
        """
        Instantiate all search algorithms with the shared price data.

        The Buy & Hold baseline is included first so its result appears
        at the top of the comparison table as a reference point.

        Returns:
            List[SearchAlgorithm]: Ready-to-run algorithm instances.
        """
        return [
            BuyAndHoldBaseline(prices=self.prices),
            BFSSearch(prices=self.prices),
            DFSSearch(prices=self.prices),
            AStarSearch(prices=self.prices),
            MinimaxSearch(prices=self.prices, max_depth=self.minimax_depth),
            AOStarSearch(prices=self.prices, max_depth=self.ao_star_depth),
        ]

    def run_all(self) -> List[SearchResult]:
        """
        Execute every algorithm with memory profiling and return results.

        For each algorithm:
            - tracemalloc is started fresh to isolate memory measurement.
            - After .search() completes, peak memory is read and stored.

        Returns:
            List[SearchResult]: One result per algorithm, with
                                peak_memory_kb populated.
        """
        algorithms: List[SearchAlgorithm] = self._build_algorithms()
        results: List[SearchResult] = []

        for algo in algorithms:
            print(f"  > Running {algo.name} ...", end=" ", flush=True)

            # ---- Memory tracking via tracemalloc ---------------------------
            # tracemalloc tracks all memory allocations made by Python.
            # We start it fresh for each algorithm to isolate measurements.
            tracemalloc.start()

            result: SearchResult = algo.search(initial_cash=self.initial_cash)

            # get_traced_memory() returns (current, peak) in bytes.
            _current_bytes, peak_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Convert peak from bytes to kilobytes for readability.
            result.peak_memory_kb = round(peak_bytes / 1024, 2)

            print(
                f"done ({result.execution_time_s:.4f}s, "
                f"{result.peak_memory_kb:.1f} KB)"
            )
            results.append(result)

        return results
