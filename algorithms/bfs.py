"""
algorithms/bfs.py — Breadth-First Search for Trading Strategy
==============================================================

AI Theory — Breadth-First Search (BFS):
    BFS is an **uninformed** (blind) search strategy that expands nodes
    in **level order** — all nodes at depth d are expanded before any
    node at depth d+1.

    Frontier Discipline: FIFO queue (first-in, first-out).

    Properties:
        - **Complete**: Yes (if the state space is finite).
        - **Optimal**:  Yes, ONLY if path cost is a non-decreasing
                        function of depth (uniform step cost).
                        In our domain, BFS finds the globally optimal
                        strategy by exhaustively comparing all terminal
                        portfolios, but it does so by expanding *every*
                        reachable state.
        - **Time**:     O(b^d) where b=branching factor, d=depth.
        - **Space**:    O(b^d) — must store the entire frontier.

    For trading:  depth = number of trading days, b ≈ 3 (BUY/SELL/HOLD).
    BFS is guaranteed to find the optimal answer but scales poorly
    compared to informed strategies like A*.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Tuple

from state import Action, State, VisitedStateTracker, get_legal_actions, transition
from algorithms.base import SearchAlgorithm, SearchResult


# ---------------------------------------------------------------------------
# BFS Internal Node
# ---------------------------------------------------------------------------

@dataclass
class _BFSNode:
    """
    Lightweight container for a node in the BFS frontier.

    Attributes:
        state   : The trading State.
        actions : The action sequence from the root to this node.
    """

    state: State
    actions: List[Action]


# ---------------------------------------------------------------------------
# BFS Algorithm
# ---------------------------------------------------------------------------

class BFSSearch(SearchAlgorithm):
    """
    Breadth-First Search adapted for trading strategy optimisation.

    Implementation Notes:
        - Uses a **FIFO deque** as the frontier.
        - Graph-search variant with VisitedStateTracker to prune duplicates.
        - Expands every reachable state layer by layer (day by day).
        - After full expansion, returns the action sequence that yields
          the *maximum* terminal portfolio value.
    """

    def __init__(self, prices: List[float]) -> None:
        super().__init__(name="BFS (Breadth-First)", prices=prices)

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Run BFS over the trading state space.

        The algorithm explores all possible decision paths day-by-day,
        collecting every terminal state, then picks the best.

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult: Best strategy found.
        """
        start_time: float = time.perf_counter()

        # ---- Initialisation ------------------------------------------------
        start_state = State(day=0, cash=initial_cash, holdings=0)
        tracker = VisitedStateTracker()
        states_explored: int = 0

        # FIFO queue — the hallmark of BFS.
        frontier: Deque[_BFSNode] = deque()
        frontier.append(_BFSNode(state=start_state, actions=[]))
        tracker.mark_visited(start_state)

        # Collect terminal (leaf) results to pick the best.
        best_value: float = -float("inf")
        best_actions: List[Action] = []

        # ---- BFS Main Loop -------------------------------------------------
        while frontier:
            node: _BFSNode = frontier.popleft()  # FIFO pop
            current: State = node.state
            states_explored += 1

            # -- Terminal check ----------------------------------------------
            if current.day >= self.num_days - 1:
                terminal_value: float = current.portfolio_value(
                    self.prices[-1]
                )
                if terminal_value > best_value:
                    best_value = terminal_value
                    best_actions = list(node.actions)
                continue

            # -- Expand successors (level-order) -----------------------------
            current_price: float = self.prices[current.day]
            for action in get_legal_actions(current):
                successor: State = transition(current, action, current_price)

                if tracker.is_visited(successor):
                    continue

                tracker.mark_visited(successor)
                frontier.append(
                    _BFSNode(
                        state=successor,
                        actions=node.actions + [action],
                    )
                )

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
    searcher = BFSSearch(prices=test_prices)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Actions          : {[a.value for a in result.best_actions]}")
    print("=" * 60)
