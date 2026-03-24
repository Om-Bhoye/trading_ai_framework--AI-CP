"""
utils.py — Data Loading & Visualisation Utilities
===================================================

Provides:
    1. CSV data loader (via pandas) for historical stock prices.
    2. ASCII table printer for terminal output.
    3. Matplotlib/Seaborn chart generators:
       a. Bar chart — Final Profit by algorithm.
       b. Scatter plot — Execution Time vs. States Explored (efficiency).

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import os
from typing import List, Optional

import pandas as pd

from algorithms.base import SearchResult


# ---------------------------------------------------------------------------
# 1. Data Loading
# ---------------------------------------------------------------------------

def load_price_data(csv_path: str) -> List[float]:
    """
    Load historical stock prices from a CSV file.

    Expected CSV format:
        Day,Price
        1,100.0
        2,105.0
        …

    Args:
        csv_path: Path to the CSV file.

    Returns:
        List[float]: Ordered list of daily stock prices.

    Raises:
        FileNotFoundError: If the CSV does not exist.
        KeyError: If the 'Price' column is missing.
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Price data file not found: {csv_path}")

    df: pd.DataFrame = pd.read_csv(csv_path)

    if "Price" not in df.columns:
        raise KeyError(
            f"CSV must contain a 'Price' column.  Found: {list(df.columns)}"
        )

    prices: List[float] = df["Price"].astype(float).tolist()
    print(f"  [OK] Loaded {len(prices)} price points from '{csv_path}'")
    return prices


# ---------------------------------------------------------------------------
# 2. ASCII Table Printer
# ---------------------------------------------------------------------------

def print_results_table(results: List[SearchResult]) -> None:
    """
    Print a clean, formatted ASCII comparison table to the terminal.

    Columns:
        Algorithm | Final Value | Profit | States | Peak Mem (KB) | Time (s) | Actions

    Args:
        results: List of SearchResult objects from the benchmark run.
    """
    # ---- Header ------------------------------------------------------------
    header = (
        f"{'Algorithm':<25} | {'Final Value':>12} | {'Profit':>10} | "
        f"{'States':>8} | {'Mem (KB)':>10} | {'Time (s)':>10} | Actions"
    )
    separator = "-" * len(header)

    print()
    print(separator)
    print("  BENCHMARK RESULTS - State-Space Search Trading Framework")
    print(separator)
    print(header)
    print("-" * 25 + "-+-" + "-" * 12 + "-+-" + "-" * 10 + "-+-"
          + "-" * 8 + "-+-" + "-" * 10 + "-+-" + "-" * 10 + "-+-"
          + "-" * 30)

    # ---- Rows --------------------------------------------------------------
    for r in results:
        actions_str: str = " -> ".join(a.value for a in r.best_actions[:8])
        if len(r.best_actions) > 8:
            actions_str += " ..."

        print(
            f"{r.algorithm_name:<25} | "
            f"${r.final_value:>10,.2f} | "
            f"${r.profit:>8,.2f} | "
            f"{r.states_explored:>8,} | "
            f"{r.peak_memory_kb:>10,.1f} | "
            f"{r.execution_time_s:>10.4f} | "
            f"{actions_str}"
        )

    print(separator)
    print()


# ---------------------------------------------------------------------------
# 3. Visualisation — Charts
# ---------------------------------------------------------------------------

def generate_charts(
    results: List[SearchResult],
    output_dir: str = ".",
) -> None:
    """
    Generate and save two publication-quality charts:

    1. **Bar Chart** — Final Profit comparison across algorithms.
    2. **Scatter Plot** — Execution Time vs. States Explored (efficiency).

    The charts are saved as PNG files in `output_dir`.

    Args:
        results    : Benchmark results.
        output_dir : Directory to save the chart images.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend for file saving.
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("  [WARN] matplotlib not installed - skipping chart generation.")
        return

    # Use a clean style.
    plt.style.use("seaborn-v0_8-darkgrid") if "seaborn-v0_8-darkgrid" in plt.style.available else None

    names: List[str] = [r.algorithm_name for r in results]
    profits: List[float] = [r.profit for r in results]
    times: List[float] = [r.execution_time_s for r in results]
    states: List[int] = [r.states_explored for r in results]

    # ---- Colour palette ----------------------------------------------------
    colors = ["#8C8C8C", "#4C72B0", "#55A868", "#C44E52", "#8172B2", "#CCB974"]

    # ======== Chart 1: Bar Chart — Final Profit =============================
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.bar(names, profits, color=colors, edgecolor="white", linewidth=1.2)

    ax1.set_title(
        "Final Profit Comparison by Algorithm",
        fontsize=16, fontweight="bold", pad=15,
    )
    ax1.set_ylabel("Profit ($)", fontsize=13)
    ax1.set_xlabel("Search Algorithm", fontsize=13)

    # Add value labels on bars.
    for bar, profit in zip(bars, profits):
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            yval + max(profits) * 0.01,
            f"${profit:,.2f}",
            ha="center", va="bottom", fontsize=10, fontweight="bold",
        )

    ax1.tick_params(axis="x", rotation=15, labelsize=10)
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    fig1.tight_layout()
    chart1_path = os.path.join(output_dir, "profit_comparison.png")
    fig1.savefig(chart1_path, dpi=150)
    plt.close(fig1)
    print(f"  [OK] Saved: {chart1_path}")

    # ======== Chart 2: Scatter — Time vs. States Explored ===================
    fig2, ax2 = plt.subplots(figsize=(10, 6))

    for i, (name, t, s) in enumerate(zip(names, times, states)):
        ax2.scatter(s, t, s=150, c=colors[i % len(colors)],
                    edgecolors="white", linewidths=1.5, zorder=5,
                    label=name)
        ax2.annotate(
            name, (s, t),
            textcoords="offset points", xytext=(8, 8),
            fontsize=9, alpha=0.85,
        )

    ax2.set_title(
        "Efficiency: Execution Time vs. States Explored",
        fontsize=16, fontweight="bold", pad=15,
    )
    ax2.set_xlabel("States Explored", fontsize=13)
    ax2.set_ylabel("Execution Time (s)", fontsize=13)
    ax2.legend(loc="best", fontsize=9, framealpha=0.9)
    fig2.tight_layout()
    chart2_path = os.path.join(output_dir, "efficiency_scatter.png")
    fig2.savefig(chart2_path, dpi=150)
    plt.close(fig2)
    print(f"  [OK] Saved: {chart2_path}")
