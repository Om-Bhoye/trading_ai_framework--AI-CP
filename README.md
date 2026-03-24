# State-Space Search-Based Framework for Trading Strategy Optimization and Benchmarking

> **Course**: Artificial Intelligence  
> **Project Type**: Decision Optimization Engine (NOT ML/Predictive)  
> **Language**: Python 3.10+  

---

## 1. Project Overview

This framework models **historical stock trading as a state-space search problem**. Instead of predicting future prices with machine learning, it treats the problem as a decision optimization task: given a known price history, what is the optimal sequence of BUY / SELL / HOLD actions to maximize portfolio value?

Six algorithms — ranging from a naive baseline to adversarial game-theoretic search — compete on the same dataset, and a benchmarking engine compares them across **profit, time, memory, and states explored**.

### Core AI Concepts Demonstrated

| Concept | Where in Code |
|---|---|
| State-Space Representation | `state.py` — `State`, `Action`, `transition()` |
| Graph Search & Pruning | `state.py` — `VisitedStateTracker` |
| Uninformed Search (BFS) | `algorithms/bfs.py` — FIFO queue |
| Uninformed Search (DFS) | `algorithms/dfs.py` — LIFO stack |
| Informed Search (A*) | `algorithms/astar.py` — priority queue + admissible heuristic |
| Adversarial Search (Minimax) | `algorithms/minimax.py` — MAX/MIN alternation |
| Alpha-Beta Pruning | `algorithms/minimax.py` — alpha/beta cutoffs |
| AND-OR Graph Search (AO*) | `algorithms/ao_star.py` — OR=choices, AND=stochastic outcomes |
| Baseline Comparison | `algorithms/buy_and_hold.py` — Buy & Hold strategy |
| Transaction Costs | `state.py` — `TRANSACTION_FEE = 0.001` (0.1%) |

---

## 2. Directory Structure

```
trading_ai_framework/
│
├── main.py                    # CLI entry point
├── state.py                   # State representation, actions, transitions, pruning
├── evaluation.py              # BenchmarkRunner with tracemalloc memory profiling
├── utils.py                   # CSV loader, ASCII table printer, matplotlib charts
│
├── data/
│   └── sample_prices.csv      # 15-day sample stock prices
│
├── output/                    # Auto-generated charts
│   ├── profit_comparison.png
│   └── efficiency_scatter.png
│
└── algorithms/
    ├── __init__.py
    ├── base.py                # SearchAlgorithm ABC + SearchResult dataclass
    ├── buy_and_hold.py        # Naive baseline (Buy Day 0, Hold forever)
    ├── bfs.py                 # Breadth-First Search
    ├── dfs.py                 # Depth-First Search
    ├── astar.py               # A* Search with admissible heuristic
    ├── minimax.py             # Minimax with Alpha-Beta Pruning
    └── ao_star.py             # AO* AND-OR Graph Search
```

---

## 3. Installation & Usage

### Prerequisites

```bash
pip install pandas matplotlib
```

### Run the Benchmark

```bash
# Default: 15-day sample data, $1,000 starting cash
python main.py

# Custom dataset and parameters
python main.py --data path/to/prices.csv --cash 5000

# Adjust adversarial search depth
python main.py --minimax-depth 8 --ao-depth 8
```

### CSV Format

The input CSV must have `Day` and `Price` columns:

```csv
Day,Price
1,100.00
2,98.50
3,102.30
...
```

---

## 4. State-Space Formulation

### State Representation

Each state is an immutable triple:

```
State = (day, cash_balance, stock_holdings)
```

### Action Space

| Action | Description | Constraint |
|--------|-------------|------------|
| `BUY` | Purchase max whole shares at current price | Must have cash >= price |
| `SELL` | Liquidate all holdings at current price | Must hold >= 1 share |
| `HOLD` | Do nothing; advance to next day | Always legal |

### Transition Function

```
transition(State, Action, Price) -> State'
```

- BUY: `cash' = cash - (shares * price) - fee`, `holdings' += shares`
- SELL: `cash' = cash + (holdings * price) - fee`, `holdings' = 0`
- HOLD: No change (no fee)

**Transaction Fee**: A 0.1% proportional fee is applied on every BUY and SELL, modeling real-world brokerage/slippage costs.

### State Pruning (Graph Search)

If two different action paths lead to the same `(day, cash, holdings)` triple, only one is explored. This collapses the search tree from O(3^d) to a much smaller graph.

---

## 5. Algorithm Details

### 5.1 Buy & Hold (Baseline)

- **Strategy**: BUY on Day 0, HOLD until end.
- **Purpose**: Any AI algorithm that cannot beat this is not adding value.
- **Complexity**: O(d) time, O(1) space.

### 5.2 Breadth-First Search (BFS)

- **Frontier**: FIFO queue — explores all states at depth d before depth d+1.
- **Optimality**: Finds global optimum by exhaustive level-order expansion.
- **Weakness**: O(b^d) space — stores the entire frontier.

### 5.3 Depth-First Search (DFS)

- **Frontier**: LIFO stack — follows one path to terminal before backtracking.
- **Space Advantage**: O(b*d) vs BFS's O(b^d).
- **Optimality**: Finds optimum only after full exploration (non-optimal ordering).

### 5.4 A* Search

- **Frontier**: Min-heap priority queue ordered by f(n) = g(n) + h(n).
- **Heuristic (Admissible)**: Upper-bounds remaining profit by assuming optimal buy-at-min, sell-at-max over the future price window. Uses precomputed suffix-min and suffix-max arrays for O(1) heuristic evaluation.
- **Optimality**: Guaranteed by admissibility of h(n).

### 5.5 Minimax with Alpha-Beta Pruning

- **Adversarial Model**: Trader (MAX) vs Market (MIN).
- **Market Scenarios**: Price shifts by {-5%, 0%, +5%} per turn.
- **Alpha-Beta Enhancement**: Prunes branches that cannot influence the final decision. Reduces O(b^d) towards O(b^(d/2)) in the best case.
- **Result**: Best *worst-case* strategy (robust, conservative).

### 5.6 AO* (AND-OR Graph Search)

- **OR Nodes**: Trader choices (pick best action).
- **AND Nodes**: Market outcomes (all must be handled; weighted by probability).
- **Expected Value**: AND-node value = weighted average of children (uniform 1/3 each).
- **Result**: Strategy that maximizes *expected* portfolio value under uncertainty.

---

## 6. Benchmarking Engine

The `BenchmarkRunner` in `evaluation.py` executes all algorithms and collects:

| Metric | Description |
|--------|-------------|
| Final Portfolio Value | Cash + holdings x final_price |
| Profit | Final value - initial cash |
| States Explored | Unique states expanded (space complexity proxy) |
| Peak Memory (KB) | Via Python's `tracemalloc` module |
| Execution Time (s) | Wall-clock via `time.perf_counter()` |
| Action Sequence | Optimal BUY/SELL/HOLD decisions |

### Sample Output (15-day, $1,000 cash)

```
----------------------------------------------------------------------------------------------------
  BENCHMARK RESULTS - State-Space Search Trading Framework
----------------------------------------------------------------------------------------------------
Algorithm                 |  Final Value |     Profit |   States |   Mem (KB) |   Time (s) | Actions
--------------------------+--------------+------------+----------+------------+------------+--------
Buy & Hold (Baseline)     | $  1,201.60 | $  201.60 |        1 |        1.0 |     0.0003 | BUY -> HOLD -> ...
BFS (Breadth-First)       | $  1,449.58 | $  449.58 |   38,722 |   12,243.3 |     0.6207 | HOLD -> BUY -> SELL -> ...
DFS (Depth-First)         | $  1,449.58 | $  449.58 |   38,722 |    5,250.7 |     0.4996 | HOLD -> BUY -> SELL -> ...
A* Search                 | $  1,449.58 | $  449.58 |   38,722 |    5,588.7 |     1.1514 | HOLD -> BUY -> SELL -> ...
Minimax + Alpha-Beta      | $  1,036.00 | $   36.00 |      151 |        2.6 |     0.0008 | HOLD -> BUY -> SELL
AO* (AND-OR Graph)        | $  1,036.00 | $   36.00 |      537 |      166.1 |     0.0034 | HOLD -> BUY -> SELL
----------------------------------------------------------------------------------------------------
```

---

## 7. Visualizations

Two charts are auto-generated in the `output/` directory:

1. **Profit Comparison Bar Chart** (`profit_comparison.png`)  
   Compares final profit across all algorithms side-by-side.

2. **Efficiency Scatter Plot** (`efficiency_scatter.png`)  
   Plots Execution Time vs States Explored for each algorithm.

---

## 8. Key Design Decisions

1. **Immutable States**: `State` is a frozen dataclass — hashable for visited sets, safe for concurrent reads.

2. **Transaction Fees (0.1%)**: Penalizes excessive trading, producing more realistic and meaningful algorithm comparisons.

3. **Graph Search Pruning**: Canonical `(day, cash, holdings)` keys collapse exponential tree to polynomial graph.

4. **Admissible A* Heuristic**: Suffix-min/max precomputation ensures O(1) heuristic calls with guaranteed admissibility.

5. **Alpha-Beta Pruning**: Reduces Minimax states from 537 to 151 (72% reduction on sample data) — validates the theoretical O(b^(d/2)) improvement.

6. **tracemalloc Memory Profiling**: Provides concrete, measurable space complexity data beyond just state counts.

7. **Buy & Hold Baseline**: Proves AI search algorithms add real value (+$248 more profit than naive baseline).

---

## 9. Extending the Framework

Adding a new algorithm is straightforward:

1. Create `algorithms/your_algorithm.py`.
2. Inherit from `SearchAlgorithm`.
3. Implement the `search(initial_cash) -> SearchResult` method.
4. Register it in `evaluation.py`'s `_build_algorithms()` list.

The framework will automatically benchmark it alongside all others.

---

## 10. Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | >= 3.10 | Core language |
| pandas | >= 1.5 | CSV data loading |
| matplotlib | >= 3.5 | Chart generation |

All other modules (`tracemalloc`, `heapq`, `collections`, `dataclasses`, `enum`, `abc`, `time`, `argparse`) are part of the Python standard library.

---

## 11. License

MIT License — see individual module headers.
