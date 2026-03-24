"""
algorithms/ — Search Algorithm Package
=======================================

This package contains all state-space search algorithm implementations
for the Trading Strategy Optimization framework.

Each algorithm inherits from `base.SearchAlgorithm` and implements the
`search()` method, returning a `SearchResult` containing the optimal
action sequence, final portfolio value, states explored, and timing data.

Available Algorithms:
    - BFS      (bfs.py)       — Breadth-First Search
    - DFS      (dfs.py)       — Depth-First Search
    - A*       (astar.py)     — A* with admissible heuristic
    - Minimax  (minimax.py)   — Adversarial search
    - AO*      (ao_star.py)   — AND-OR graph search
"""

from algorithms.base import SearchAlgorithm, SearchResult

__all__ = ["SearchAlgorithm", "SearchResult"]
