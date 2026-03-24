"""
algorithms/dfs.py — Depth-First Search for Trading Strategy
============================================================

AI Theory — Depth-First Search (DFS):
    DFS is an **uninformed** search strategy that always expands the
    **deepest** unexpanded node first, following a single decision path
    all the way to the terminal state before backtracking.

    Frontier Discipline: LIFO stack (last-in, first-out).

    Properties:
        - **Complete**: Yes (in finite state spaces with cycle detection).
        - **Optimal**:  NO — DFS does not guarantee finding the best
                        solution first.  It finds *a* solution quickly,
                        then must continue searching to prove optimality.
                        We implement it to exhaustively cover all paths
                        so we can compare its exploration pattern to BFS.
        - **Time**:     O(b^d) in the worst case.
        - **Space**:    O(b × d) — only stores one path + siblings,
                        significantly better than BFS's O(b^d).

    For trading: DFS's space advantage makes it viable for longer price
    series, but it explores the state space in a very different *order*
    than BFS, which is pedagogically interesting to observe.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import time
from typing import List

from state import Action, State, VisitedStateTracker, get_legal_actions, transition
from algorithms.base import SearchAlgorithm, SearchResult


class DFSSearch(SearchAlgorithm):
    """
    Depth-First Search adapted for trading strategy optimisation.

    Implementation Notes:
        - Uses an explicit **LIFO stack** (Python list with append/pop).
        - Graph-search variant with visited-state pruning.
        - Explores a full path to the terminal day before backtracking.
        - Tracks the best terminal portfolio across all explored paths.
    """

    def __init__(self, prices: List[float]) -> None:
        super().__init__(name="DFS (Depth-First)", prices=prices)

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Run DFS over the trading state space.

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult: Best strategy found after full exploration.
        """
        start_time: float = time.perf_counter()

        # ---- Initialisation ------------------------------------------------
        start_state = State(day=0, cash=initial_cash, holdings=0)
        tracker = VisitedStateTracker()
        states_explored: int = 0

        # LIFO stack — the hallmark of DFS.
        # Each element: (State, List[Action])
        stack: List[tuple] = [(start_state, [])]

        best_value: float = -float("inf")
        best_actions: List[Action] = []

        # ---- DFS Main Loop -------------------------------------------------
        while stack:
            current, actions = stack.pop()  # LIFO pop (deepest node first)

            if tracker.is_visited(current):
                continue

            tracker.mark_visited(current)
            states_explored += 1

            # -- Terminal check ----------------------------------------------
            if current.day >= self.num_days - 1:
                terminal_value: float = current.portfolio_value(
                    self.prices[-1]
                )
                if terminal_value > best_value:
                    best_value = terminal_value
                    best_actions = list(actions)
                continue

            # -- Expand successors (push onto stack — LIFO) ------------------
            current_price: float = self.prices[current.day]
            for action in get_legal_actions(current):
                successor: State = transition(current, action, current_price)

                if not tracker.is_visited(successor):
                    stack.append((successor, actions + [action]))

        # ---- Build result --------------------------------------------------
        elapsed: float = time.perf_counter() - start_time

        result = SearchResult(
            algorithm_name=self.name,
            best_actions=best_actions,
            final_value=round(best_value, 2),
            states_explored=states_explored,
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
    searcher = DFSSearch(prices=test_prices)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Actions          : {[a.value for a in result.best_actions]}")
    print("=" * 60)
