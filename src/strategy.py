"""
S&P 500 Trend Allocator — signal generation and portfolio construction.
Deterministic: identical inputs produce identical outputs.
No side effects, no I/O, no randomness.
"""
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Indicators
# ---------------------------------------------------------------------------

def _log_momentum(closes: np.ndarray, lookback: int) -> Optional[float]:
    """Log-return over `lookback` bars. None if history is insufficient."""
    if len(closes) < lookback + 1:
        return None
    past, present = closes[-(lookback + 1)], closes[-1]
    if past <= 0 or present <= 0:
        return None
    return math.log(present / past)


def _above_sma(closes: np.ndarray, period: int) -> bool:
    """True if the last close is above the N-bar simple moving average."""
    if len(closes) < period:
        return False
    return bool(closes[-1] > np.mean(closes[-period:]))


def _atr_pct(df_sym: pd.DataFrame, lookback: int) -> float:
    """Average true range as a fraction of last close (volatility proxy)."""
    hi = df_sym["high"].values
    lo = df_sym["low"].values
    cl = df_sym["close"].values
    if len(cl) < 2:
        return float("inf")
    tr = [
        max(hi[i] - lo[i], abs(hi[i] - cl[i - 1]), abs(lo[i] - cl[i - 1]))
        for i in range(1, len(cl))
    ]
    atr = float(np.mean(tr[-lookback:])) if tr else float("inf")
    last = float(cl[-1])
    return atr / last if last > 0 else float("inf")


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

def compute_signals(
    bars_df: pd.DataFrame,
    cfg: dict,
    tradeable_symbols: List[str],
) -> pd.DataFrame:
    """
    Compute trend/momentum signals for each symbol.

    Returns DataFrame indexed by symbol with columns:
      close, momentum_fast, momentum_slow, above_trend_sma, atr_pct, score, eligible
    """
    fast_lb = int(cfg["fast_lookback"])
    slow_lb = int(cfg["slow_lookback"])
    trend_lb = int(cfg["trend_lookback"])
    atr_lb = int(cfg["atr_lookback"])
    min_fast = float(cfg["min_momentum_6m"])
    min_slow = float(cfg["min_momentum_12m"])

    available = set(bars_df.index.get_level_values("symbol"))
    rows = []

    for sym in tradeable_symbols:
        if sym not in available:
            continue
        df_sym = bars_df.loc[sym].sort_index()
        closes = df_sym["close"].values
        if len(closes) < 2:
            continue
        rows.append(
            {
                "symbol": sym,
                "close": float(closes[-1]),
                "momentum_fast": _log_momentum(closes, fast_lb),
                "momentum_slow": _log_momentum(closes, slow_lb),
                "above_trend_sma": _above_sma(closes, trend_lb),
                "atr_pct": _atr_pct(df_sym, atr_lb),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=["close", "momentum_fast", "momentum_slow",
                     "above_trend_sma", "atr_pct", "score", "eligible"]
        )

    df = pd.DataFrame(rows).set_index("symbol")

    # Ensure float dtype so fillna comparisons don't produce object-dtype warnings
    df["momentum_fast"] = pd.to_numeric(df["momentum_fast"], errors="coerce")
    df["momentum_slow"] = pd.to_numeric(df["momentum_slow"], errors="coerce")

    has_both = df["momentum_fast"].notna() & df["momentum_slow"].notna()
    fast_ok = df["momentum_fast"].fillna(-999.0) >= min_fast
    slow_ok = df["momentum_slow"].fillna(-999.0) >= min_slow
    finite_atr = df["atr_pct"] < float("inf")

    df["eligible"] = df["above_trend_sma"] & has_both & fast_ok & slow_ok & finite_atr
    df["score"] = (
        df["momentum_fast"].fillna(-999.0) + df["momentum_slow"].fillna(-999.0)
    )
    df.loc[~df["eligible"], "score"] = -999.0
    return df


# ---------------------------------------------------------------------------
# Regime (breadth)
# ---------------------------------------------------------------------------

def compute_breadth(
    bars_df: pd.DataFrame,
    universe_symbols: List[str],
    trend_lookback: int,
) -> float:
    """Fraction of universe symbols above their N-bar SMA."""
    available = set(bars_df.index.get_level_values("symbol"))
    n_above = n_total = 0
    for sym in universe_symbols:
        if sym not in available:
            continue
        closes = bars_df.loc[sym].sort_index()["close"].values
        if len(closes) < trend_lookback:
            continue
        n_total += 1
        if closes[-1] > np.mean(closes[-trend_lookback:]):
            n_above += 1
    return n_above / n_total if n_total > 0 else 0.0


# ---------------------------------------------------------------------------
# Portfolio construction
# ---------------------------------------------------------------------------

def build_portfolio(
    signals_df: pd.DataFrame,
    breadth: float,
    cfg: dict,
    sector_map: dict,
    fallback_symbol: str = "BIL",
) -> Dict[str, float]:
    """
    Construct target portfolio weights {symbol: weight}.
    Weights sum to <= equity_budget. Cash fills the rest.

    Risk-off: breadth < threshold → all equity budget to fallback.
    Risk-on: inverse-ATR weighting with sector caps, position cap, exposure cap.
    """
    equity_alloc = float(cfg["risk_on_equity_alloc"])
    cash_buf = float(cfg["cash_buffer"])
    max_gross = float(cfg["max_gross_exposure"])
    max_holdings = int(cfg["max_holdings"])
    max_weight = float(cfg["max_position_weight"])
    max_per_sector = int(cfg["max_names_per_sector"])
    threshold = float(cfg["breadth_threshold"])

    equity_budget = min(equity_alloc, max_gross - cash_buf)

    if breadth < threshold:
        return {fallback_symbol: round(equity_budget, 6)}

    eligible = signals_df[signals_df["eligible"]].sort_values("score", ascending=False)
    if eligible.empty:
        return {fallback_symbol: round(equity_budget, 6)}

    # Sector-capped selection
    selected: List[Tuple[str, float]] = []
    sector_counts: Dict[str, int] = {}
    for sym, row in eligible.iterrows():
        sector = sector_map.get(sym, "Unknown")
        if sector.startswith("_"):
            continue
        count = sector_counts.get(sector, 0)
        if count >= max_per_sector:
            continue
        selected.append((sym, float(row["atr_pct"])))
        sector_counts[sector] = count + 1
        if len(selected) >= max_holdings:
            break

    if not selected:
        return {fallback_symbol: round(equity_budget, 6)}

    # Inverse-ATR weighting: lower vol → higher weight
    inv_atrs = [1.0 / max(atr, 1e-4) for _, atr in selected]
    total_inv = sum(inv_atrs)

    weights: Dict[str, float] = {}
    for (sym, _), inv_a in zip(selected, inv_atrs):
        weights[sym] = min((inv_a / total_inv) * equity_budget, max_weight)

    # Scale down if position caps caused overshoot
    total = sum(weights.values())
    if total > equity_budget and total > 0:
        weights = {s: w * equity_budget / total for s, w in weights.items()}

    # Drop hairline weights (< 0.5% of portfolio)
    return {s: round(w, 6) for s, w in weights.items() if w >= 0.005}
