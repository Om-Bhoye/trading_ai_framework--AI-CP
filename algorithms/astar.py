"""
algorithms/astar.py — A* Search for Optimal Trading Strategy
=============================================================

AI Theory — A* Search:
    A* is a **best-first graph search** algorithm that expands the node
    with the lowest evaluation function f(n):

        f(n) = g(n) + h(n)

    where:
        g(n) = cost from the start state to node n  (path cost so far).
        h(n) = heuristic estimate of the cost from n to the goal.

    Optimality Guarantee:
        A* is guaranteed to find an optimal solution if the heuristic h(n)
        is **admissible** — meaning it NEVER overestimates the true cost
        to reach the goal.

    Adaptation for Trading:
        Since we are *maximising* portfolio value rather than *minimising*
        cost, we negate values so that standard min-heap priority works:

        g(n) = –(portfolio_value achieved so far)
             → We want to *maximise* value, so lower g ↔ higher value.

        h(n) = –(upper bound on *additional* profit possible from day n
                 to the end of the timeline).

        This upper bound is computed by assuming we could **buy at the
        lowest future price** and **sell at the highest future price**
        in the remaining window, which clearly never underestimates
        the best-case remaining profit ⟹ admissible.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from state import Action, State, VisitedStateTracker, get_legal_actions, transition
from algorithms.base import SearchAlgorithm, SearchResult


# ---------------------------------------------------------------------------
# Heuristic Function
# ---------------------------------------------------------------------------

def admissible_heuristic(
    state: State,
    prices: List[float],
    precomputed_max: List[float],
    precomputed_min: List[float],
) -> float:
    """
    Compute an **admissible** heuristic for the remaining profit potential.

    Design Rationale (Admissibility Proof Sketch):
        From the current state we ask: "What is the *theoretical maximum*
        additional profit the agent could earn from day `state.day` onward?"

        Upper bound = max possible portfolio value at the terminal day
                    − current portfolio value.

        We estimate the max possible terminal value as:
            best_case = cash + holdings × max_future_price              ... (A)
                      + (cash // min_future_price) × max_future_price   ... (B)

        (A) Values the existing holdings at the highest future price.
        (B) Assumes we could buy at the cheapest future price and sell
            at the highest, earning the maximum possible trading gain.

        Since both (A) and (B) are *best-case* assumptions that ignore
        the single-step-per-day constraint, the resulting h(n) is an
        **overestimate of remaining profit** — which, when negated into
        cost form, is an **underestimate of remaining cost** ⟹ admissible.

    Args:
        state           : Current trading state.
        prices          : Full price series.
        precomputed_max : precomputed_max[i] = max(prices[i:])
        precomputed_min : precomputed_min[i] = min(prices[i:])

    Returns:
        float: Upper bound on additional profit achievable (≥ 0).
    """
    day: int = state.day

    # ---- Terminal / out-of-range check -------------------------------------
    if day >= len(prices):
        return 0.0

    # ---- Look-ahead price extremes -----------------------------------------
    max_future_price: float = precomputed_max[day]
    min_future_price: float = precomputed_min[day]

    # ---- Current portfolio value at today's price --------------------------
    current_value: float = state.portfolio_value(prices[day])

    # ---- Optimistic terminal portfolio calculation -------------------------
    # Scenario: Sell existing holdings at the *highest* future price,
    # then buy at the *lowest* future price and sell at the *highest*.
    best_from_holdings: float = state.holdings * max_future_price
    best_from_cash: float = state.cash  # keep cash as-is for the buy below

    # How many shares could we theoretically buy at the cheapest price?
    if min_future_price > 0:
        theoretical_shares: int = int(state.cash // min_future_price)
        best_from_cash = (
            state.cash
            - theoretical_shares * min_future_price
            + theoretical_shares * max_future_price
        )

    optimistic_terminal_value: float = best_from_holdings + best_from_cash
    additional_profit: float = optimistic_terminal_value - current_value

    # Clamp at 0: heuristic should not predict *loss* as "useful".
    return max(additional_profit, 0.0)


# ---------------------------------------------------------------------------
# A* Node (for the priority queue)
# ---------------------------------------------------------------------------

@dataclass(order=True)
class _AStarNode:
    """
    Internal priority-queue node for A*.

    Ordering:
        Nodes are ordered by `f_neg` = –f(n) = –(g(n) + h(n)).
        Since Python's heapq is a *min-heap* and we want to *maximise*
        portfolio value, we negate so that the node with the *highest*
        expected value is popped first.

    Attributes:
        f_neg         : Negated f-value (for min-heap ordering).
        state         : The trading State at this node.
        actions       : The action sequence from root to this node.
        portfolio_val : g(n) = current portfolio value (unnegated).
    """

    f_neg: float
    state: State = field(compare=False)
    actions: List[Action] = field(compare=False)
    portfolio_val: float = field(compare=False)


# ---------------------------------------------------------------------------
# A* Search Algorithm
# ---------------------------------------------------------------------------

class AStarSearch(SearchAlgorithm):
    """
    A* Search adapted for trading strategy optimisation.

    AI Theory Highlights:
        - **Frontier**: min-heap priority queue ordered by f(n).
        - **Closed Set**: VisitedStateTracker prevents re-expansion.
        - **Optimality**: Guaranteed by admissible heuristic.
        - **Completeness**: Guaranteed (finite state space).

    The search terminates when the frontier node with the highest
    f-value is a terminal state (day == len(prices) - 1), meaning
    no remaining actions can improve upon it.
    """

    def __init__(self, prices: List[float]) -> None:
        """
        Initialise A* with a price series.

        Also precompute suffix-max and suffix-min arrays for O(1)
        heuristic evaluation at every node.

        Args:
            prices: Historical daily stock prices.
        """
        super().__init__(name="A* Search", prices=prices)

        # ---- Precompute suffix extremes for heuristic ----------------------
        n: int = len(prices)
        self._suffix_max: List[float] = [0.0] * n
        self._suffix_min: List[float] = [float("inf")] * n

        self._suffix_max[-1] = prices[-1]
        self._suffix_min[-1] = prices[-1]

        for i in range(n - 2, -1, -1):
            self._suffix_max[i] = max(prices[i], self._suffix_max[i + 1])
            self._suffix_min[i] = min(prices[i], self._suffix_min[i + 1])

    # ---- Main search method ------------------------------------------------

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Execute A* search to find the optimal trading action sequence.

        Algorithm Pseudocode:
            1. Create start node with g = portfolio_value, h = heuristic.
            2. Push onto min-heap (negated for max behaviour).
            3. Loop:
                a. Pop node with lowest f_neg (highest f).
                b. If terminal day → record as best and return.
                c. If already visited → skip (graph search).
                d. Else mark visited, expand successors:
                   For each legal action:
                       - Compute successor state via transition().
                       - Compute g' and h' for successor.
                       - Push successor node onto heap.
            4. Return the best result found.

        Args:
            initial_cash: Starting cash balance.

        Returns:
            SearchResult: Optimal strategy and associated metrics.
        """
        start_time: float = time.perf_counter()

        # ---- Initialisation ------------------------------------------------
        start_state = State(day=0, cash=initial_cash, holdings=0)
        tracker = VisitedStateTracker()
        states_explored: int = 0

        # g(start) = current portfolio value at day-0 price
        g_start: float = start_state.portfolio_value(self.prices[0])

        # h(start) = admissible upper-bound on remaining profit
        h_start: float = admissible_heuristic(
            start_state, self.prices, self._suffix_max, self._suffix_min
        )

        f_start: float = g_start + h_start

        start_node = _AStarNode(
            f_neg=-f_start,
            state=start_state,
            actions=[],
            portfolio_val=g_start,
        )

        # ---- Priority queue (min-heap on f_neg) ----------------------------
        frontier: List[_AStarNode] = []
        heapq.heappush(frontier, start_node)

        # ---- Best solution tracking ----------------------------------------
        best_value: float = -float("inf")
        best_actions: List[Action] = []

        # ---- Main A* loop --------------------------------------------------
        while frontier:
            node: _AStarNode = heapq.heappop(frontier)
            current_state: State = node.state

            # -- Graph-search duplicate check --------------------------------
            if tracker.is_visited(current_state):
                continue

            tracker.mark_visited(current_state)
            states_explored += 1

            # -- Terminal state check ----------------------------------------
            # We define "terminal" as reaching the last day in the series.
            if current_state.day >= self.num_days - 1:
                # Evaluate final portfolio at the last known price.
                terminal_price: float = self.prices[-1]
                terminal_value: float = current_state.portfolio_value(
                    terminal_price
                )

                if terminal_value > best_value:
                    best_value = terminal_value
                    best_actions = list(node.actions)

                # Continue searching — with graph-search pruning, we
                # must check all distinct terminal states to ensure
                # global optimality.
                continue

            # -- Expand successors -------------------------------------------
            current_price: float = self.prices[current_state.day]
            for action in get_legal_actions(current_state):
                successor: State = transition(
                    current_state, action, current_price
                )

                if tracker.is_visited(successor):
                    continue

                # g(successor) = portfolio value at successor's day
                if successor.day < self.num_days:
                    g_succ: float = successor.portfolio_value(
                        self.prices[successor.day]
                    )
                else:
                    g_succ = successor.portfolio_value(self.prices[-1])

                # h(successor) = admissible heuristic
                h_succ: float = admissible_heuristic(
                    successor,
                    self.prices,
                    self._suffix_max,
                    self._suffix_min,
                )

                f_succ: float = g_succ + h_succ

                successor_node = _AStarNode(
                    f_neg=-f_succ,
                    state=successor,
                    actions=node.actions + [action],
                    portfolio_val=g_succ,
                )

                heapq.heappush(frontier, successor_node)

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
    # Quick test with a small price series.
    test_prices: List[float] = [100, 90, 105, 95, 110, 120, 115]

    searcher = AStarSearch(prices=test_prices)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Initial Cash     : ${result.initial_cash:,.2f}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Action Sequence  : {[a.value for a in result.best_actions]}")
    print("=" * 60)
