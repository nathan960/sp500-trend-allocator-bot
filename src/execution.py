"""
Order execution: compute trade list and submit with all safety gates.
Sells always precede buys (frees buying power first).
No orders when DRY_RUN=true (the default).
"""
from typing import Dict, List, Tuple

from src.alpaca_client import AlpacaClient, AlpacaError
from src.data import spread_ok
from src.risk import (
    RiskViolation,
    assert_gross_exposure_ok,
    assert_market_open,
    is_dry_run,
    passes_min_notional,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def current_weights(positions: list, equity: float) -> Dict[str, float]:
    """Convert Alpaca positions list → {symbol: portfolio_weight}."""
    if equity <= 0:
        return {}
    return {
        p["symbol"]: float(p["market_value"]) / equity
        for p in positions
        if float(p.get("market_value", 0)) > 0
    }


def open_order_symbols(orders: list) -> set:
    """Symbols with an active (non-terminal) open order."""
    active = {"new", "partially_filled", "accepted", "pending_new", "held"}
    return {o["symbol"] for o in orders if o.get("status") in active}


# ---------------------------------------------------------------------------
# Trade computation
# ---------------------------------------------------------------------------

def compute_trades(
    cur_weights: Dict[str, float],
    target_weights: Dict[str, float],
    equity: float,
    cfg: dict,
) -> Tuple[List[dict], List[dict]]:
    """
    Compute the sell and buy orders needed to move from cur_weights → target_weights.

    Returns (sells, buys) — both sorted largest-notional-first.
    Only trades with drift > rebalance_threshold and notional > min_notional are included.
    """
    rebalance_threshold = float(cfg["rebalance_threshold"])
    sells: List[dict] = []
    buys: List[dict] = []

    for sym in sorted(set(cur_weights) | set(target_weights)):
        cur = cur_weights.get(sym, 0.0)
        tgt = target_weights.get(sym, 0.0)
        if abs(tgt - cur) < rebalance_threshold:
            continue
        notional = abs(tgt - cur) * equity
        if not passes_min_notional(notional, cfg):
            continue
        trade = {
            "symbol": sym,
            "notional": notional,
            "current_weight": cur,
            "target_weight": tgt,
            "side": "sell" if tgt < cur else "buy",
        }
        (sells if tgt < cur else buys).append(trade)

    sells.sort(key=lambda x: x["notional"], reverse=True)
    buys.sort(key=lambda x: x["notional"], reverse=True)
    return sells, buys


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def execute_rebalance(
    client: AlpacaClient,
    sells: List[dict],
    buys: List[dict],
    positions: list,
    equity: float,
    cfg: dict,
    quotes_raw: dict = None,
) -> List[dict]:
    """
    Submit sell and buy orders (sells first).
    Applies all safety gates: market clock, gross exposure, duplicate-order,
    min notional, and spread checks on buys.
    When DRY_RUN=true returns dry-run records; no network writes occur.
    """
    dry = is_dry_run()

    clock = client.get_clock()
    if not dry:
        assert_market_open(clock)
    elif not clock.get("is_open", False):
        print(f"  [warn] Market is closed (DRY_RUN — continuing for simulation)")

    assert_gross_exposure_ok(positions, equity, cfg)

    open_syms = open_order_symbols(client.get_orders())
    position_map = {p["symbol"]: p for p in positions}
    max_spread = float(cfg.get("max_spread_bps", 100))

    results: List[dict] = []

    # -- Sells (use qty) --
    for trade in sells:
        sym = trade["symbol"]
        base = {k: trade[k] for k in ("symbol", "side", "notional",
                                        "current_weight", "target_weight")}
        if sym in open_syms:
            results.append({**base, "status": "skipped_open_order"})
            continue

        pos = position_map.get(sym)
        if not pos:
            results.append({**base, "status": "skipped_no_position"})
            continue

        cur_qty = float(pos.get("qty", 0))
        tgt = trade["target_weight"]
        if tgt <= 0:
            qty_to_sell = cur_qty
        else:
            price = float(pos.get("current_price", 0))
            qty_to_sell = (
                min(round(trade["notional"] / price, 6), cur_qty) if price > 0 else cur_qty
            )

        if qty_to_sell <= 0:
            results.append({**base, "status": "skipped_zero_qty"})
            continue

        if dry:
            results.append({**base, "qty": qty_to_sell, "status": "dry_run"})
        else:
            try:
                resp = client.submit_sell_qty(sym, qty_to_sell)
                results.append({**base, "qty": qty_to_sell,
                                 "status": "submitted", "order_id": resp.get("id")})
            except (AlpacaError, Exception) as exc:
                results.append({**base, "status": f"error: {exc}"})

    # -- Buys (use notional) --
    for trade in buys:
        sym = trade["symbol"]
        base = {k: trade[k] for k in ("symbol", "side", "notional",
                                        "current_weight", "target_weight")}
        if sym in open_syms:
            results.append({**base, "status": "skipped_open_order"})
            continue

        if not passes_min_notional(trade["notional"], cfg):
            results.append({**base, "status": "skipped_min_notional"})
            continue

        # Spread gate (permissive if no quote data)
        if quotes_raw and not spread_ok(quotes_raw, sym, max_spread):
            results.append({**base, "status": "skipped_wide_spread"})
            continue

        if dry:
            results.append({**base, "status": "dry_run"})
        else:
            try:
                resp = client.submit_buy_notional(sym, trade["notional"])
                results.append({**base, "status": "submitted",
                                 "order_id": resp.get("id")})
            except (AlpacaError, Exception) as exc:
                results.append({**base, "status": f"error: {exc}"})

    return results
