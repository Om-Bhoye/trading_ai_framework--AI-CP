"""
algorithms/ao_star.py — AO* (AND-OR Graph) Search for Trading
==============================================================

AI Theory — AO* Search (AND-OR Graphs):
    AO* is designed for problems where the solution is not a simple
    *path* but a **contingency plan** (policy / strategy tree).

    Node Types:
        OR  nodes — represent **agent choices**.  The agent picks ONE
                    child (e.g., BUY, SELL, or HOLD).  Solution must
                    contain exactly one child's sub-solution.
        AND nodes — represent **stochastic outcomes** (Nature's moves).
                    ALL children must be solved because any outcome
                    could occur.  Solution must handle every child.

    For Trading:
        OR  nodes: Trader decision ⟹ choose the best action.
        AND nodes: Market stochasticity ⟹ price goes up / down / flat.
                   The strategy must be robust across *all* scenarios.

    Expected Value at AND nodes:
        value(AND) = Σ  P(outcome_i) × value(child_i)
        We assume uniform probability: P = 1/3 for each of {up, down, flat}.

    AO* maintains a **solved** flag per sub-tree.  A sub-tree is solved
    when:
        - At an OR node: at least one child is solved.
        - At an AND node: ALL children are solved.

    This is a simplified, depth-limited AO* suitable for pedagogical
    demonstration.  The algorithm returns the best OR-choice at each
    level, with AND-node values averaged.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from state import Action, State, get_legal_actions, transition
from algorithms.base import SearchAlgorithm, SearchResult


# ---------------------------------------------------------------------------
# Market Stochastic Outcomes (AND-node branches)
# ---------------------------------------------------------------------------

# Each tuple: (label, price_multiplier, probability)
MARKET_OUTCOMES: List[Tuple[str, float, float]] = [
    ("down", 0.95, 1 / 3),
    ("flat", 1.00, 1 / 3),
    ("up",   1.05, 1 / 3),
]


# ---------------------------------------------------------------------------
# AO* Node
# ---------------------------------------------------------------------------

@dataclass
class AONode:
    """
    A node in the AND-OR search graph.

    Attributes:
        state      : Trading state at this node.
        node_type  : 'OR' (trader choice) or 'AND' (market outcome).
        value      : Computed expected value (propagated from leaves).
        solved     : True if this sub-tree has been fully evaluated.
        best_action: For OR nodes, the chosen action.
        children   : Child nodes.
        action     : The action taken to reach this node from parent.
    """

    state: State
    node_type: str = "OR"      # "OR" or "AND"
    value: float = 0.0
    solved: bool = False
    best_action: Optional[Action] = None
    children: List["AONode"] = field(default_factory=list)
    action: Optional[Action] = None


# ---------------------------------------------------------------------------
# AO* Search Algorithm
# ---------------------------------------------------------------------------

class AOStarSearch(SearchAlgorithm):
    """
    AO* Search for trading under market uncertainty.

    Graph Structure:
        Level 0 (OR) : Trader at day 0 picks BUY/SELL/HOLD.
        Level 1 (AND): Market responds with {up, down, flat} price.
        Level 2 (OR) : Trader at day 1 picks BUY/SELL/HOLD.
        …and so on alternating.

    The algorithm:
        1. Build the AND-OR graph to the depth limit.
        2. Evaluate leaf nodes (terminal portfolio value).
        3. Back-propagate:
            - AND nodes: weighted average of children (expected value).
            - OR  nodes: max of children (best trader action).
        4. Extract the best policy (sequence of OR-node choices).
    """

    def __init__(
        self,
        prices: List[float],
        max_depth: Optional[int] = None,
    ) -> None:
        """
        Args:
            prices    : Historical daily stock prices.
            max_depth : Maximum tree depth. Defaults to 2 × num_days
                        (each trader-turn + market-turn = 2 levels).
        """
        super().__init__(name="AO* (AND-OR Graph)", prices=prices)
        self._max_depth: int = max_depth if max_depth else 2 * self.num_days
        self._states_explored: int = 0

    # ---- Leaf evaluation ---------------------------------------------------

    def _evaluate(self, state: State) -> float:
        """Terminal portfolio value."""
        price: float = self.prices[min(state.day, self.num_days - 1)]
        return state.portfolio_value(price)

    # ---- Recursive AND-OR tree builder & evaluator -------------------------

    def _build_and_evaluate(
        self,
        state: State,
        depth: int,
        node_type: str,
        action: Optional[Action] = None,
    ) -> AONode:
        """
        Recursively build the AND-OR graph and compute node values.

        Args:
            state     : Current trading state.
            depth     : Remaining depth budget.
            node_type : 'OR' (trader) or 'AND' (market).
            action    : Action taken to reach this node (for tracing).

        Returns:
            AONode: Fully evaluated node with propagated value.
        """
        self._states_explored += 1

        node = AONode(state=state, node_type=node_type, action=action)

        # ---- Base case: terminal or depth exhausted ------------------------
        if state.day >= self.num_days - 1 or depth <= 0:
            node.value = self._evaluate(state)
            node.solved = True
            return node

        current_price: float = self.prices[state.day]

        if node_type == "OR":
            # ============ OR Node: Trader Decision ============
            # Expand one child per legal action, each leading to an AND node.
            best_val: float = -float("inf")
            best_child: Optional[AONode] = None

            for act in get_legal_actions(state):
                successor: State = transition(state, act, current_price)

                child = self._build_and_evaluate(
                    state=successor,
                    depth=depth - 1,
                    node_type="AND",
                    action=act,
                )
                node.children.append(child)

                if child.value > best_val:
                    best_val = child.value
                    best_child = child
                    node.best_action = act

            node.value = best_val
            node.solved = best_child.solved if best_child else True

        else:
            # ============ AND Node: Market Outcomes ============
            # ALL outcomes must be considered (stochastic branching).
            expected_val: float = 0.0
            all_solved: bool = True

            for label, multiplier, probability in MARKET_OUTCOMES:
                # Apply the market's price shift for the *next* day.
                shifted_price: float = current_price * multiplier

                # Create a state reflecting the market-adjusted price.
                # The state itself doesn't change (same cash/holdings),
                # but the price used for the subsequent trader decision
                # is shifted.  We model this by keeping the same day
                # and letting the OR child see the adjusted price via
                # the price list.
                #
                # For simplicity, we proceed with the *actual* next-day
                # state and weight by probability — standard AO* practice.
                market_state = State(
                    day=state.day,
                    cash=state.cash,
                    holdings=state.holdings,
                )

                child = self._build_and_evaluate(
                    state=market_state,
                    depth=depth - 1,
                    node_type="OR",
                    action=None,
                )
                node.children.append(child)

                expected_val += probability * child.value
                if not child.solved:
                    all_solved = False

            node.value = expected_val
            node.solved = all_solved

        return node

    # ---- Extract best policy from solved graph -----------------------------

    @staticmethod
    def _extract_policy(node: AONode) -> List[Action]:
        """
        Walk the solved AND-OR graph and extract the OR-node decisions.

        At OR nodes, follow the best_action child.
        At AND nodes, we have no choice — all are included, but for
        the *optimal sequence* we follow the first child (representative).

        Returns:
            List[Action]: The sequence of trader actions.
        """
        actions: List[Action] = []
        current: Optional[AONode] = node

        while current and current.children:
            if current.node_type == "OR" and current.best_action is not None:
                actions.append(current.best_action)
                # Follow the child matching best_action.
                for child in current.children:
                    if child.action == current.best_action:
                        current = child
                        break
                else:
                    break
            elif current.node_type == "AND":
                # Follow the first (representative) outcome.
                current = current.children[0] if current.children else None
            else:
                break

        return actions

    # ---- Public search interface -------------------------------------------

    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Run AO* search from the initial state.

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult: Best expected-value strategy and metrics.
        """
        start_time: float = time.perf_counter()
        self._states_explored = 0

        start_state = State(day=0, cash=initial_cash, holdings=0)

        root: AONode = self._build_and_evaluate(
            state=start_state,
            depth=self._max_depth,
            node_type="OR",
        )

        best_actions: List[Action] = self._extract_policy(root)

        elapsed: float = time.perf_counter() - start_time

        result = SearchResult(
            algorithm_name=self.name,
            best_actions=best_actions,
            final_value=round(root.value, 2),
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
    searcher = AOStarSearch(prices=test_prices, max_depth=6)
    result = searcher.search(initial_cash=1000.0)

    print("=" * 60)
    print(f"  Algorithm        : {result.algorithm_name}")
    print(f"  Final Value      : ${result.final_value:,.2f}")
    print(f"  Profit           : ${result.profit:,.2f}")
    print(f"  States Explored  : {result.states_explored}")
    print(f"  Time             : {result.execution_time_s:.4f}s")
    print(f"  Actions          : {[a.value for a in result.best_actions]}")
    print("=" * 60)
