"""
state.py — State Space & Environment Modeling
==============================================

This module defines the core state representation for modeling historical
stock trading as a **state-space search problem**.

AI Theory:
    In state-space search, we define:
        - A **State**: A snapshot of the world at a given point.
        - An **Action Space**: The set of legal moves from any given state.
        - A **Transition Function**: A deterministic mapping
          (State, Action) → State' that produces the successor state.
        - **State Pruning**: Mechanisms (visited sets, memoization) to
          collapse duplicate states reached via different paths, preventing
          the combinatorial explosion inherent in exhaustive search.

    For this trading framework:
        State  = (current_day, cash_balance, stock_holdings)
        Action = {BUY, SELL, HOLD}
        Transition is governed by the stock price on `current_day`.

Author : Framework Team
License: MIT
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Transaction Cost Configuration
# ---------------------------------------------------------------------------

# A small proportional fee applied to every BUY or SELL transaction.
# This models realistic brokerage/slippage costs and penalises excessive
# trading, encouraging algorithms to find strategies with fewer, more
# impactful trades.  Set to 0.0 to disable.
TRANSACTION_FEE: float = 0.001   # 0.1% per transaction


# ---------------------------------------------------------------------------
# Action Space Definition
# ---------------------------------------------------------------------------

class Action(enum.Enum):
    """
    Enumeration of all legal trading actions.

    In state-space search terminology, these are the **operators** that
    transform one state into a successor state.

    BUY  — Spend all available cash to purchase stock at the current price.
    SELL — Liquidate all stock holdings into cash at the current price.
    HOLD — Take no action; advance to the next day with the same portfolio.
    """

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


# ---------------------------------------------------------------------------
# State Representation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class State:
    """
    Immutable snapshot of the trading environment at a specific point in time.

    AI Theory — State Representation:
        A well-designed state must capture **all information** required to
        make future decisions, without carrying redundant data.  We encode:

        - `day`      : The temporal position in the price timeline (0-indexed).
        - `cash`     : Available liquid capital (rounded to 2 dp for hashing).
        - `holdings` : Number of shares currently held (integer).

    The state is *frozen* (immutable) so it can be hashed and stored in
    visited sets for duplicate detection / graph-search pruning.

    Attributes:
        day      (int)  : Current day index in the price series.
        cash     (float): Available cash balance (USD).
        holdings (int)  : Number of stock shares held.
    """

    day: int
    cash: float
    holdings: int

    # ---- Canonical key for memoization / visited-set pruning ---------------

    def canonical_key(self) -> Tuple[int, float, int]:
        """
        Return a hashable canonical form of this state.

        State Pruning Theory:
            If two different action sequences lead to the *same*
            (day, cash, holdings) triple, the future is identical
            regardless of how we arrived here.  We therefore only need
            to explore one of them.  The canonical key is the identity
            used by visited sets to detect and prune such duplicates.

        We round cash to 2 decimal places to avoid floating-point
        artifacts causing logically identical states to appear distinct.

        Returns:
            Tuple[int, float, int]: (day, rounded_cash, holdings)
        """
        return (self.day, round(self.cash, 2), self.holdings)

    # ---- Portfolio valuation -----------------------------------------------

    def portfolio_value(self, current_price: float) -> float:
        """
        Compute the total portfolio value (cash + equity) at the given price.

        This is the primary **objective function** that search algorithms
        aim to maximise.

        Args:
            current_price: The stock price on the current day.

        Returns:
            float: Total portfolio value = cash + (holdings × price).
        """
        return self.cash + self.holdings * current_price

    # ---- Pretty printing ---------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"State(day={self.day}, cash=${self.cash:,.2f}, "
            f"holdings={self.holdings})"
        )


# ---------------------------------------------------------------------------
# Transition Function
# ---------------------------------------------------------------------------

def get_legal_actions(state: State) -> List[Action]:
    """
    Return the list of *legal* actions from the given state.

    Action Legality Constraints:
        - BUY  is legal only if the agent has enough cash to purchase
          at least 1 share at the current price.  (Checked externally
          since price is needed; here we include BUY optimistically
          and let the transition function handle 0-share buys.)
        - SELL is legal only if the agent holds ≥ 1 share.
        - HOLD is always legal.

    Args:
        state: The current State.

    Returns:
        List[Action]: Legal actions from this state.
    """
    actions: List[Action] = [Action.HOLD]

    # SELL is only meaningful if we own shares.
    if state.holdings > 0:
        actions.append(Action.SELL)

    # BUY is always *syntactically* offered; the transition function
    # will gate it against the actual price (cash >= price).
    actions.append(Action.BUY)

    return actions


def transition(
    state: State,
    action: Action,
    price: float,
) -> State:
    """
    Deterministic transition function:  (State, Action, Price) -> State'.

    AI Theory -- Transition Model:
        The transition function is the **physics of the world**.  Given the
        current state and an action chosen by the agent, it produces the
        unique successor state.  In our domain the transition also depends
        on an *exogenous* variable -- the stock price -- which is read from
        the historical dataset (no prediction is involved).

    Transaction Costs:
        A proportional fee (TRANSACTION_FEE = 0.1%) is deducted from cash
        on every BUY or SELL action.  This models real-world brokerage and
        slippage costs, penalising strategies that trade excessively.

    Rules:
        BUY  -> Purchase as many whole shares as affordable at `price`.
               cost      = shares_bought * price
               fee       = cost * TRANSACTION_FEE
               cash'     = cash - cost - fee
               holdings' = holdings + shares_bought
        SELL -> Liquidate ALL holdings at `price`.
               revenue   = holdings * price
               fee       = revenue * TRANSACTION_FEE
               cash'     = cash + revenue - fee
               holdings' = 0
        HOLD -> No change in cash or holdings (no fee applied).

    The successor state always advances to `day + 1`.

    Args:
        state  : Current State.
        action : The chosen Action.
        price  : Stock price on `state.day`.

    Returns:
        State: The resulting successor state on day+1.
    """
    new_day: int = state.day + 1

    if action == Action.BUY:
        # ---------- BUY Logic ----------
        # Determine max whole shares affordable, accounting for fee.
        effective_price: float = price * (1.0 + TRANSACTION_FEE)
        shares_to_buy: int = int(state.cash // effective_price) if price > 0 else 0

        if shares_to_buy == 0:
            # Cannot afford even 1 share -> effectively a HOLD.
            return State(day=new_day, cash=state.cash, holdings=state.holdings)

        cost: float = shares_to_buy * price
        fee: float = cost * TRANSACTION_FEE       # 0.1% fee on purchase
        return State(
            day=new_day,
            cash=round(state.cash - cost - fee, 2),
            holdings=state.holdings + shares_to_buy,
        )

    elif action == Action.SELL:
        # ---------- SELL Logic ----------
        # Liquidate entire position at the current price, minus fee.
        revenue: float = state.holdings * price
        fee: float = revenue * TRANSACTION_FEE    # 0.1% fee on sale
        return State(
            day=new_day,
            cash=round(state.cash + revenue - fee, 2),
            holdings=0,
        )

    else:
        # ---------- HOLD Logic ----------
        return State(day=new_day, cash=state.cash, holdings=state.holdings)


# ---------------------------------------------------------------------------
# State Pruning Utilities
# ---------------------------------------------------------------------------

class VisitedStateTracker:
    """
    Efficient visited-state set for **graph-search** pruning.

    AI Theory — Graph Search vs. Tree Search:
        In *tree search*, every path from the root is explored independently,
        leading to O(b^d) nodes where b = branching factor, d = depth.
        *Graph search* maintains a **closed set** of already-expanded states.
        If a newly generated state matches one in the closed set, it is
        discarded.  This can reduce the search space from exponential to
        polynomial in many domains.

        For our trading problem:
        - Branching factor b ≈ 3 (BUY, SELL, HOLD).
        - Depth d = number of trading days.
        - Without pruning: O(3^d) states.
        - With pruning: at most O(d × C × H) states where C and H are
          the number of distinct cash/holdings values reachable, which is
          drastically smaller.

    Usage:
        tracker = VisitedStateTracker()
        if not tracker.is_visited(state):
            tracker.mark_visited(state)
            # … expand state …
    """

    def __init__(self) -> None:
        """Initialise an empty visited set."""
        self._visited: Set[Tuple[int, float, int]] = set()

    def is_visited(self, state: State) -> bool:
        """
        Check whether an equivalent state has already been explored.

        Args:
            state: The State to check.

        Returns:
            bool: True if a state with the same canonical key was visited.
        """
        return state.canonical_key() in self._visited

    def mark_visited(self, state: State) -> None:
        """
        Record a state as explored.

        Args:
            state: The State to mark.
        """
        self._visited.add(state.canonical_key())

    @property
    def count(self) -> int:
        """Return the number of unique states visited so far."""
        return len(self._visited)

    def reset(self) -> None:
        """Clear all visited records (useful between algorithm runs)."""
        self._visited.clear()


# ---------------------------------------------------------------------------
# Module Self-Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Quick smoke test to verify state transitions.
    prices = [100.0, 105.0, 95.0, 110.0, 102.0]

    initial = State(day=0, cash=1000.0, holdings=0)
    print(f"Initial : {initial}")

    # BUY on day 0 @ $100 → 10 shares, $0 cash
    s1 = transition(initial, Action.BUY, prices[0])
    print(f"After BUY  @ ${prices[0]}: {s1}")

    # HOLD on day 1
    s2 = transition(s1, Action.HOLD, prices[1])
    print(f"After HOLD @ ${prices[1]}: {s2}")

    # SELL on day 2 @ $95 → 0 shares, $950 cash
    s3 = transition(s2, Action.SELL, prices[2])
    print(f"After SELL @ ${prices[2]}: {s3}")

    # Portfolio value check
    print(f"Portfolio value on day 3 @ ${prices[3]}: "
          f"${s3.portfolio_value(prices[3]):,.2f}")

    # Visited tracker test
    tracker = VisitedStateTracker()
    tracker.mark_visited(initial)
    print(f"\nInitial visited? {tracker.is_visited(initial)}")  # True

    duplicate = State(day=0, cash=1000.0, holdings=0)
    print(f"Duplicate visited? {tracker.is_visited(duplicate)}")  # True

    different = State(day=0, cash=999.0, holdings=0)
    print(f"Different visited? {tracker.is_visited(different)}")  # False
    print(f"Total states tracked: {tracker.count}")
