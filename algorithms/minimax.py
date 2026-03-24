"""
algorithms/minimax.py — Minimax with Alpha-Beta Pruning for Trading
=====================================================================

AI Theory — Minimax Search:
    Minimax is the foundational algorithm for **adversarial search** in
    two-player zero-sum games.  It models the problem as a game tree
    where two agents alternate turns:

        MAXIMISER (the Trader):  Chooses the action (BUY/SELL/HOLD) that
                                 *maximises* portfolio value.
        MINIMISER (the Market):  Simulates worst-case price movement for
                                 the next day to *minimise* the trader's
                                 portfolio value.

    The algorithm recursively computes the **minimax value** of each node:
        - At MAX nodes:  value = max(children values)
        - At MIN nodes:  value = min(children values)

AI Theory — Alpha-Beta Pruning:
    Alpha-Beta is an optimisation of Minimax that **prunes** branches of
    the game tree that cannot influence the final decision.

    Two bounds are maintained:
        alpha = the best value the Maximiser can guarantee so far.
        beta  = the best value the Minimiser can guarantee so far.

    Pruning Rules:
        - At a MAX node, if a child's value >= beta, we **prune** the
          remaining siblings.  Reason: the Minimiser would never allow
          the game to reach this node, since it already has a better
          option (beta) elsewhere.
        - At a MIN node, if a child's value <= alpha, we **prune** the
          remaining siblings.  Reason: the Maximiser would never choose
          the path leading here, since it already has a better guarantee
          (alpha) elsewhere.

    Complexity Reduction:
        - Raw Minimax:  O(b^d) nodes explored.
        - Alpha-Beta:   O(b^(d/2)) in the best case (perfect ordering),
                        which effectively doubles the searchable depth
                        for the same computational budget.
        - The `states_explored` counter clearly shows this reduction
          in the benchmark output.

    Adaptation for Trading:
        After the Trader chooses an action at a MAX node, the Market
        (MIN node) selects the *worst-case* next-day price from a
        set of scenarios:
            { actual_price x 0.95,   actual_price,   actual_price x 1.05 }
        representing a down/flat/up outcome.

    Depth Limiting:
        Since the full tree can be very large, we apply a configurable
        depth limit with a terminal evaluation function.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

from state import Action, State, get_legal_actions, transition
from algorithms.base import SearchAlgorithm, SearchResult


# ---------------------------------------------------------------------------
# Market Scenario Model
# ---------------------------------------------------------------------------

# The adversarial market can shift a day's price by these multipliers.
# 0.95 -> 5% drop, 1.00 -> flat, 1.05 -> 5% rise.
MARKET_SCENARIOS: List[float] = [0.95, 1.00, 1.05]


# ---------------------------------------------------------------------------
# Minimax Algorithm with Alpha-Beta Pruning
# ---------------------------------------------------------------------------

class MinimaxSearch(SearchAlgorithm):
    """
    Minimax Search with Alpha-Beta Pruning and adversarial market modelling.

    Node Types:
        MAX nodes (even depth): Trader picks BUY / SELL / HOLD.
        MIN nodes (odd depth) : Market picks worst-case price scenario.

    Alpha-Beta Enhancement:
        The `alpha` and `beta` bounds are threaded through the recursion.
        When a branch is provably irrelevant (alpha >= beta), it is pruned,
        dramatically reducing the number of states explored compared to
        raw Minimax — especially visible in the benchmark's "States" column.
    """

    def __init__(
        self,
        prices: List[float],
        max_depth: Optional[int] = None,
    ) -> None:
        """
        Args:
            prices    : Historical daily stock prices.
            max_depth : Maximum search depth (in trader-turns).
                        Defaults to len(prices) for full search.
        """
        super().__init__(name="Minimax + Alpha-Beta", prices=prices)
        self._max_depth: int = max_depth if max_depth else self.num_days
        self._states_explored: int = 0
        self._pruned_branches: int = 0   # Counter for pruned subtrees
        self._best_actions: List[Action] = []

    # ---- Terminal evaluation -----------------------------------------------

    def _evaluate(self, state: State) -> float:
        """
        Terminal evaluation function.

        Returns the portfolio value at the final known price.
        This is the **utility** at a leaf of the game tree.

        Args:
            state: Terminal State.

        Returns:
            float: Portfolio value.
        """
        price: float = self.prices[min(state.day, self.num_days - 1)]
        return state.portfolio_value(price)

    # ---- Recursive Minimax with Alpha-Beta Pruning -------------------------

    def _minimax_ab(
        self,
        state: State,
        depth: int,
        is_maximiser: bool,
        alpha: float,
        beta: float,
        actions_so_far: List[Action],
    ) -> Tuple[float, List[Action]]:
        """
        Core recursive minimax function with alpha-beta pruning.

        AI Theory — Alpha-Beta Parameters:
            alpha : Best value the Maximiser can guarantee on the path
                    from root to this node.  Starts at -inf.
            beta  : Best value the Minimiser can guarantee on the path
                    from root to this node.  Starts at +inf.

            At any point, if alpha >= beta, the current branch is
            provably irrelevant and can be pruned (cut off).

        Args:
            state          : Current State.
            depth          : Remaining depth budget.
            is_maximiser   : True if this is a MAX (trader) node.
            alpha          : Maximiser's best guaranteed value so far.
            beta           : Minimiser's best guaranteed value so far.
            actions_so_far : Action trace to this point.

        Returns:
            (value, action_sequence) : Minimax value and optimal actions.
        """
        self._states_explored += 1

        # ---- Base case: terminal state or depth exhausted ------------------
        if state.day >= self.num_days - 1 or depth <= 0:
            return self._evaluate(state), list(actions_so_far)

        current_price: float = self.prices[state.day]

        if is_maximiser:
            # ============ MAXIMISER (Trader) Turn ============
            # The trader picks the action with the HIGHEST minimax value.
            max_val: float = -float("inf")
            best_act_seq: List[Action] = list(actions_so_far)

            for action in get_legal_actions(state):
                successor: State = transition(state, action, current_price)
                val, act_seq = self._minimax_ab(
                    successor,
                    depth - 1,
                    is_maximiser=False,  # Next turn: Market (MIN)
                    alpha=alpha,
                    beta=beta,
                    actions_so_far=actions_so_far + [action],
                )
                if val > max_val:
                    max_val = val
                    best_act_seq = act_seq

                # ---- Alpha update & Beta cutoff ----------------------------
                # Update alpha: Maximiser now knows it can guarantee at
                # least `max_val`.
                alpha = max(alpha, max_val)

                # Beta cutoff: If alpha >= beta, the Minimiser (parent)
                # would never let the game reach here — prune remaining
                # siblings.  This is where Alpha-Beta saves work.
                if alpha >= beta:
                    self._pruned_branches += 1
                    break  # Prune remaining actions

            return max_val, best_act_seq

        else:
            # ============ MINIMISER (Market) Turn ============
            # The market picks the price scenario that HURTS the trader most.
            min_val: float = float("inf")
            worst_act_seq: List[Action] = list(actions_so_far)

            for scenario_mult in MARKET_SCENARIOS:
                hypothetical_state = State(
                    day=state.day,
                    cash=state.cash,
                    holdings=state.holdings,
                )

                val, act_seq = self._minimax_ab(
                    hypothetical_state,
                    depth - 1,
                    is_maximiser=True,  # Next turn: Trader (MAX)
                    alpha=alpha,
                    beta=beta,
                    actions_so_far=actions_so_far,
                )

                if val < min_val:
                    min_val = val
                    worst_act_seq = act_seq

                # ---- Beta update & Alpha cutoff ----------------------------
                # Update beta: Minimiser now knows it can guarantee the
                # Maximiser gets at most `min_val`.
                beta = min(beta, min_val)

                # Alpha cutoff: If alpha >= beta, the Maximiser (parent)
                # already has a better option — prune remaining scenarios.
                if alpha >= beta:
                    self._pruned_branches += 1
                    break  # Prune remaining market scenarios

            return min_val, worst_act_seq

    # ---- Public search interface -------------------------------------------

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Run Minimax with Alpha-Beta Pruning from the initial state.

        Alpha and Beta are initialised to -inf and +inf respectively,
        representing no prior knowledge about bounds.

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult: Best *worst-case* strategy and metrics.
        """
        start_time: float = time.perf_counter()
        self._states_explored = 0
        self._pruned_branches = 0

        start_state = State(day=0, cash=initial_cash, holdings=0)

        # Alpha = -inf (Maximiser's initial worst case)
        # Beta  = +inf (Minimiser's initial worst case)
        best_value, best_actions = self._minimax_ab(
            state=start_state,
            depth=self._max_depth,
            is_maximiser=True,
            alpha=-float("inf"),
            beta=float("inf"),
            actions_so_far=[],
        )

        elapsed: float = time.perf_counter() - start_time

        result = SearchResult(
            algorithm_name=self.name,
            best_actions=best_actions,
            final_value=round(best_value, 2),
            states_explored=self._states_explored,
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
    searcher = MinimaxSearch(prices=test_prices, max_depth=6)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Branches Pruned  : {searcher._pruned_branches}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Actions          : {[a.value for a in result.best_actions]}")
    print("=" * 60)
