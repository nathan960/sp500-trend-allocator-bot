"""
Risk guards: all raise RiskViolation when a constraint is breached.
Parameters come from the strategy cfg dict rather than hardcoded constants.
"""
import os
from typing import Dict


class RiskViolation(Exception):
    """Raised when any risk constraint is breached."""


# ---------------------------------------------------------------------------
# Environment / mode guards
# ---------------------------------------------------------------------------

def is_dry_run() -> bool:
    """True if DRY_RUN env var is 'true' (the default)."""
    return os.environ.get("DRY_RUN", "true").lower() == "true"


def assert_live_confirmed() -> None:
    """Raise if TRADING_MODE=live without LIVE_TRADING_CONFIRMED=true."""
    mode = os.environ.get("TRADING_MODE", "paper").lower()
    confirmed = os.environ.get("LIVE_TRADING_CONFIRMED", "false").lower() == "true"
    if mode == "live" and not confirmed:
        raise RiskViolation(
            "TRADING_MODE=live requires LIVE_TRADING_CONFIRMED=true."
        )


# ---------------------------------------------------------------------------
# Market clock
# ---------------------------------------------------------------------------

def assert_market_open(clock: dict) -> None:
    """Raise RiskViolation if Alpaca clock says the market is closed."""
    if not clock.get("is_open", False):
        raise RiskViolation(
            f"Market is closed. Next open: {clock.get('next_open', 'unknown')}. "
            "No orders outside market hours."
        )


# ---------------------------------------------------------------------------
# Portfolio-level guards
# ---------------------------------------------------------------------------

def assert_drawdown_ok(equity: float, high_water_mark: float, cfg: dict) -> None:
    """Raise if drawdown from HWM exceeds cfg['max_drawdown_pct']."""
    max_dd = float(cfg.get("max_drawdown_pct", 0.20))
    if high_water_mark <= 0:
        return
    dd = (high_water_mark - equity) / high_water_mark
    if dd > max_dd:
        raise RiskViolation(
            f"Portfolio drawdown {dd:.1%} > limit {max_dd:.1%}. "
            "Manual intervention required."
        )


def assert_daily_loss_ok(equity: float, day_start_equity: float, cfg: dict) -> None:
    """Raise if today's loss exceeds cfg['max_daily_loss_pct']."""
    max_daily = float(cfg.get("max_daily_loss_pct", 0.05))
    if day_start_equity <= 0:
        return
    loss = (day_start_equity - equity) / day_start_equity
    if loss > max_daily:
        raise RiskViolation(
            f"Daily loss {loss:.1%} > limit {max_daily:.1%}. "
            "No new orders today."
        )


def assert_gross_exposure_ok(
    positions: list, equity: float, cfg: dict, tolerance: float = 0.02
) -> None:
    """Raise if gross long exposure exceeds cfg['max_gross_exposure'] + tolerance."""
    if equity <= 0:
        return
    max_gross = float(cfg.get("max_gross_exposure", 0.95))
    gross = sum(
        float(p.get("market_value", 0))
        for p in positions
        if float(p.get("market_value", 0)) > 0
    )
    exposure = gross / equity
    if exposure > max_gross + tolerance:
        raise RiskViolation(
            f"Gross exposure {exposure:.1%} > limit {max_gross:.1%}."
        )


def assert_sector_caps_ok(
    target_weights: Dict[str, float],
    sector_map: dict,
    cfg: dict,
) -> None:
    """Raise if the plan's target weights violate sector caps."""
    max_per_sector = int(cfg.get("max_names_per_sector", 3))
    counts: Dict[str, int] = {}
    for sym, w in target_weights.items():
        if w <= 0:
            continue
        sector = sector_map.get(sym, "Unknown")
        if sector.startswith("_"):
            continue
        counts[sector] = counts.get(sector, 0) + 1
        if counts[sector] > max_per_sector:
            raise RiskViolation(
                f"Sector cap violation in plan: {sector} has >{max_per_sector} positions "
                f"(offender: {sym})."
            )


# ---------------------------------------------------------------------------
# Order-level guards
# ---------------------------------------------------------------------------

def passes_min_notional(notional: float, cfg: dict) -> bool:
    """False = skip this order (too small)."""
    return notional >= float(cfg.get("min_notional_usd", 25))


# ---------------------------------------------------------------------------
# Per-position stop guards (software-managed exits)
# ---------------------------------------------------------------------------

def is_stop_loss_triggered(price: float, avg_entry: float, cfg: dict) -> bool:
    """True if position fell >= stop_loss_pct below entry."""
    if avg_entry <= 0:
        return False
    return (avg_entry - price) / avg_entry >= float(cfg.get("stop_loss_pct", 0.20))


def is_trailing_stop_triggered(price: float, peak_price: float, cfg: dict) -> bool:
    """True if position fell >= trailing_stop_pct from its peak."""
    if peak_price <= 0:
        return False
    return (peak_price - price) / peak_price >= float(cfg.get("trailing_stop_pct", 0.35))


# ---------------------------------------------------------------------------
# Cost estimate
# ---------------------------------------------------------------------------

def round_trip_cost_bps(cfg: dict) -> float:
    """Estimated total round-trip cost in bps."""
    return (
        float(cfg.get("fee_bps", 0))
        + float(cfg.get("slippage_bps", 5))
        + float(cfg.get("spread_buffer_bps", 5))
    )
