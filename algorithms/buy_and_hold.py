"""
algorithms/buy_and_hold.py — Buy & Hold Baseline Strategy
==========================================================

Purpose — Extensibility & Baseline Comparison:
    This simple algorithm does NOT perform any search.  It implements the
    classic **Buy & Hold** investment strategy:

        1. On Day 0, buy as many shares as possible with the starting cash.
        2. Hold all shares until the final day.

    It serves two important roles in the framework:

    A) **Baseline Benchmark**: Every AI search algorithm should
       outperform this naive strategy to demonstrate that the
       search-based optimisation is actually adding value.

    B) **Extensibility Proof**: Demonstrates that the `SearchAlgorithm`
       abstract base class is flexible enough to accommodate non-search
       strategies, proving the framework's modular design.

    The "states explored" is always 1 (the initial state) since no
    search is performed.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import time
from typing import List

from state import Action, State, transition
from algorithms.base import SearchAlgorithm, SearchResult


class BuyAndHoldBaseline(SearchAlgorithm):
    """
    Buy & Hold — the simplest possible trading strategy.

    Strategy:
        Day 0: BUY (spend all cash on shares).
        Day 1 … Day N-1: HOLD.

    This deterministic strategy requires no tree/graph search and runs
    in O(d) time where d = number of trading days (just a linear walk).

    The result provides a baseline profit figure.  Any AI algorithm that
    cannot beat Buy & Hold is arguably not useful for this dataset.
    """

    def __init__(self, prices: List[float]) -> None:
        super().__init__(name="Buy & Hold (Baseline)", prices=prices)

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Execute the Buy & Hold strategy (no search needed).

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult: Strategy result with baseline metrics.
        """
        start_time: float = time.perf_counter()

        # ---- Build the action sequence ------------------------------------
        # BUY on day 0, HOLD for every subsequent day.
        actions: List[Action] = [Action.BUY]
        actions.extend([Action.HOLD] * (self.num_days - 2))

        # ---- Simulate the strategy step-by-step --------------------------
        state = State(day=0, cash=initial_cash, holdings=0)

        for i, action in enumerate(actions):
            price: float = self.prices[state.day]
            state = transition(state, action, price)

        # ---- Final portfolio valuation ------------------------------------
        final_price: float = self.prices[-1]
        final_value: float = state.portfolio_value(final_price)

        elapsed: float = time.perf_counter() - start_time

        result = SearchResult(
            algorithm_name=self.name,
            best_actions=actions,
            final_value=round(final_value, 2),
            states_explored=1,          # No search — only one path.
            execution_time_s=round(elapsed, 6),
            initial_cash=initial_cash,
        )
        result.compute_profit()
        return result


# ---------------------------------------------------------------------------
# Module Self-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_prices = [100, 90, 105, 95, 110, 120, 115]
    searcher = BuyAndHoldBaseline(prices=test_prices)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Actions          : {[a.value for a in result.best_actions]}")
    print("=" * 60)
