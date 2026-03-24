"""
algorithms/base.py — Abstract Base Class for Search Algorithms
==============================================================

AI Theory — Uniform Interface for Search:
    All classical search algorithms share a common skeleton:
        1. Initialise a frontier with the start state.
        2. Loop: pick a state from the frontier, expand it, add successors.
        3. Terminate when a goal state is reached or the frontier is empty.

    The *only* thing that changes across BFS, DFS, A*, etc. is the
    **frontier discipline** (FIFO, LIFO, priority queue) and the
    **evaluation function** used to order the frontier.

    This base class captures that shared contract so that every algorithm
    can be benchmarked through an identical API.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from state import Action, State


# ---------------------------------------------------------------------------
# Search Result Data Container
# ---------------------------------------------------------------------------

@dataclass
class SearchResult:
    """
    Standard container returned by every algorithm after search completion.

    Attributes:
        algorithm_name    (str)          : Human-readable algorithm label.
        best_actions      (List[Action]) : Optimal action sequence found.
        final_value       (float)        : Terminal portfolio value ($).
        states_explored   (int)          : Total unique states expanded
                                           (space-complexity proxy).
        execution_time_s  (float)        : Wall-clock time in seconds.
        initial_cash      (float)        : Starting cash for reference.
        profit            (float)        : final_value − initial_cash.
    """

    algorithm_name: str = ""
    best_actions: List[Action] = field(default_factory=list)
    final_value: float = 0.0
    states_explored: int = 0
    execution_time_s: float = 0.0
    initial_cash: float = 0.0
    profit: float = 0.0
    peak_memory_kb: float = 0.0

    def compute_profit(self) -> None:
        """Derive profit from final_value and initial_cash."""
        self.profit = round(self.final_value - self.initial_cash, 2)


# ---------------------------------------------------------------------------
# Abstract Search Algorithm
# ---------------------------------------------------------------------------

class SearchAlgorithm(abc.ABC):
    """
    Abstract base class that all search strategies must implement.

    AI Theory — Strategy Pattern:
        By programming to an interface (`search()`) rather than a concrete
        class, we can swap algorithms freely in the benchmarking engine.
        Each subclass encodes a different **frontier discipline** and
        **evaluation function**, making the theoretical mechanics of each
        algorithm highly visible and distinct.

    Attributes:
        name   (str)         : Display name of the algorithm.
        prices (List[float]) : Historical price series (index = day).
    """

    def __init__(self, name: str, prices: List[float]) -> None:
        """
        Initialise the base algorithm.

        Args:
            name   : Human-readable name (e.g. "A* Search").
            prices : List of daily stock prices.
        """
        self.name: str = name
        self.prices: List[float] = prices
        self.num_days: int = len(prices)

    @abc.abstractmethod
    def search(self, initial_cash: float = 1000.0) -> SearchResult:
        """
        Execute the search from an initial state and return the result.

        Every subclass MUST implement this method.

        Args:
            initial_cash: Starting cash balance.

        Returns:
            SearchResult: Populated result with metrics and action trace.
        """
        ...

    # ---- Shared helper: timed execution wrapper ----------------------------

    def _timed_search(self, initial_cash: float) -> SearchResult:
        """
        Wrapper that times the `search()` method.  Subclasses typically
        call `_run_search()` internally and this wrapper is unused, but
        it is provided for convenience.

        Args:
            initial_cash: Starting cash.

        Returns:
            SearchResult with execution_time_s populated.
        """
        start: float = time.perf_counter()
        result: SearchResult = self.search(initial_cash)
        result.execution_time_s = time.perf_counter() - start
        return result
