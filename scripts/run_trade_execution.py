#!/usr/bin/env python3
"""
Stage 2: Trade Execution.

Reads data/latest/trade_plan.json, verifies all safety gates, then submits
Alpaca paper orders to move the portfolio toward the target weights.

Safety gates (all must pass before any order is submitted):
  1. Plan exists and is not stale (< 90 min old)
  2. Plan is approved
  3. LIVE_TRADING_CONFIRMED=true if TRADING_MODE=live
  4. Market clock is open (warn only if DRY_RUN=true)
  5. Drawdown guard
  6. Daily-loss guard
  7. Gross-exposure guard
  8. Sector-cap verification
  9. No duplicate open orders for affected symbols
  10. Min notional per order
  11. Spread gate for buy orders

DRY_RUN=true (default): prints what would happen, no orders submitted.
DRY_RUN=false + TRADING_MODE=paper: submits paper orders.
TRADING_MODE=live: blocked unless LIVE_TRADING_CONFIRMED=true.

Usage:
  DRY_RUN=true  TRADING_MODE=paper python scripts/run_trade_execution.py
  DRY_RUN=false TRADING_MODE=paper python scripts/run_trade_execution.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.alpaca_client import AlpacaClient, AlpacaError
from src.data import _is_feed_permission_error
from src.execution import compute_trades, current_weights, execute_rebalance
from src.plan import PlanError, read_plan, verify_approved, verify_freshness
from src.reporting import append_trade_log, print_positions, print_trades, print_account_summary
from src.risk import (
    RiskViolation,
    assert_daily_loss_ok,
    assert_drawdown_ok,
    assert_live_confirmed,
    assert_sector_caps_ok,
    is_dry_run,
)
from src.state import (
    load_state,
    save_state,
    set_last_run,
    update_day_start,
    update_high_water_mark,
)


def load_config():
    root = Path(__file__).parent.parent
    with open(root / "config" / "strategy.json") as f:
        raw = json.load(f)
    cfg = raw["parameters"]
    with open(root / "config" / "sector_map.json") as f:
        sector_map = json.load(f)
    return cfg, sector_map


def main():
    cfg, sector_map = load_config()
    dry = is_dry_run()
    mode_tag = "DRY_RUN" if dry else "LIVE_PAPER"

    print("=" * 60)
    print(f"Stage 2: Trade Execution  [{mode_tag}]")
    print("=" * 60)

    # ---- Gate: live trading confirmation ----
    try:
        assert_live_confirmed()
    except RiskViolation as e:
        print(f"\n[BLOCKED] {e}")
        sys.exit(1)

    # ---- Read and verify plan ----
    print("\n[plan] Reading trade_plan.json...")
    try:
        plan = read_plan()
        verify_freshness(plan)
        verify_approved(plan)
    except PlanError as e:
        print(f"\n[BLOCKED] Plan verification failed: {e}")
        sys.exit(1)

    target_weights = plan["target_weights"]
    regime = plan.get("regime", "?").upper()
    breadth = plan.get("breadth", 0.0)
    plan_hash = plan.get("data_hash", "?")
    print(f"  Regime: {regime}  Breadth: {breadth:.1%}  Hash: {plan_hash}")
    print(f"  Target weights: {list(target_weights.keys())}")

    # ---- Gate: sector caps in plan ----
    try:
        assert_sector_caps_ok(target_weights, sector_map, cfg)
    except RiskViolation as e:
        print(f"\n[BLOCKED] {e}")
        sys.exit(1)

    # ---- Fetch live account state ----
    print("\n[account] Fetching live account state...")
    client = AlpacaClient()
    account = client.get_account()
    positions = client.get_positions()
    orders = client.get_orders()
    clock = client.get_clock()
    equity = float(account["equity"])

    print_account_summary(account)
    print(f"  Market: {'OPEN' if clock.get('is_open') else 'CLOSED'}")

    # ---- State: HWM and day-start ----
    state = load_state()
    state = update_high_water_mark(state, equity)
    state = update_day_start(state, equity)

    hwm = float(state.get("high_water_mark", equity))
    day_start = float(state.get("day_start_equity", equity))

    # ---- Gate: drawdown and daily-loss ----
    try:
        assert_drawdown_ok(equity, hwm, cfg)
    except RiskViolation as e:
        print(f"\n[BLOCKED] {e}")
        state = set_last_run(state, "trade_execution")
        save_state(state)
        sys.exit(1)

    try:
        assert_daily_loss_ok(equity, day_start, cfg)
    except RiskViolation as e:
        print(f"\n[BLOCKED] {e}")
        state = set_last_run(state, "trade_execution")
        save_state(state)
        sys.exit(1)

    drawdown = (hwm - equity) / hwm if hwm > 0 else 0.0
    daily_loss = (day_start - equity) / day_start if day_start > 0 else 0.0
    print(f"\n[risk] Drawdown: {drawdown:.2%}  Daily loss: {daily_loss:.2%}  HWM: ${hwm:,.2f}")

    # ---- Compute trades ----
    cur = current_weights(positions, equity)
    sells, buys = compute_trades(cur, target_weights, equity, cfg)

    print(f"\n[trades] Proposed: {len(sells)} sells, {len(buys)} buys")
    print_trades(sells, buys)

    if not sells and not buys:
        print("\n[done] No trades to execute.")
        state = set_last_run(state, "trade_execution")
        save_state(state)
        return

    # ---- Fetch latest quotes for spread check on buys ----
    buy_symbols = [t["symbol"] for t in buys]
    quotes_raw = {}
    if buy_symbols:
        try:
            quotes_raw = client.get_latest_quotes(buy_symbols)
        except AlpacaError as e:
            if _is_feed_permission_error(str(e)):
                print(f"\n[BLOCKED] Quote feed '{client.data_feed}' returned a subscription/permission error. "
                      f"Set ALPACA_DATA_FEED to a supported feed. Error: {e}")
                sys.exit(1)
            print(f"  [warn] Quote fetch failed (non-feed error): {e} — spread check disabled for buys")
        except Exception as e:
            print(f"  [warn] Quote fetch failed: {e} — spread check disabled for buys")

    # ---- Execute (all gates inside execute_rebalance) ----
    print(f"\n[execute] Submitting orders [{mode_tag}]...")
    results = execute_rebalance(
        client, sells, buys, positions, equity, cfg, quotes_raw=quotes_raw
    )

    submitted = [r for r in results if r["status"] == "submitted"]
    dry_results = [r for r in results if r["status"] == "dry_run"]
    skipped = [r for r in results if r["status"].startswith("skipped")]
    errors = [r for r in results if r["status"].startswith("error")]

    print(f"  Submitted: {len(submitted)}  Dry-run: {len(dry_results)}  "
          f"Skipped: {len(skipped)}  Errors: {len(errors)}")
    for r in results:
        sym = r["symbol"]
        side = r["side"].upper()
        status = r["status"]
        notional = r.get("notional", 0)
        qty = r.get("qty", "")
        detail = f"qty={qty}" if qty else f"notional=${notional:,.0f}"
        print(f"  {side:5} {sym:8} {detail:>20}  [{status}]")

    if errors:
        print(f"\n  [warn] {len(errors)} order(s) errored — see above")

    # ---- Append trade log ----
    append_trade_log(results, plan, equity, dry)
    print("\n[log] Appended memory/TRADE-LOG.md")

    state = set_last_run(state, "trade_execution")
    save_state(state)

    action = "No orders submitted (DRY_RUN)." if dry else f"{len(submitted)} order(s) submitted to Alpaca paper."
    print(f"\n[done] Stage 2 complete. {action}")


if __name__ == "__main__":
    main()
