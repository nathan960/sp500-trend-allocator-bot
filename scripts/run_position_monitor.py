#!/usr/bin/env python3
"""
Position monitor: live account state, stop-loss scan, and drift vs target.
Read-only. No orders submitted.

Usage:
  DRY_RUN=true python scripts/run_position_monitor.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

os.environ["DRY_RUN"] = "true"

from src.alpaca_client import AlpacaClient
from src.data import check_stale, get_bars_df
from src.execution import compute_trades, current_weights, open_order_symbols
from src.reporting import print_account_summary, print_positions, print_trades
from src.risk import (
    assert_daily_loss_ok,
    assert_drawdown_ok,
    is_stop_loss_triggered,
    is_trailing_stop_triggered,
)
from src.state import (
    get_trailing_high,
    load_state,
    save_state,
    set_last_run,
    update_day_start,
    update_high_water_mark,
    update_trailing_high,
)
from src.strategy import build_portfolio, compute_breadth, compute_signals


def load_config():
    root = Path(__file__).parent.parent
    with open(root / "config" / "strategy.json") as f:
        raw = json.load(f)
    cfg = raw["parameters"]
    with open(root / "config" / "universe.json") as f:
        uni = json.load(f)
    with open(root / "config" / "sector_map.json") as f:
        sector_map = json.load(f)
    return cfg, uni, sector_map


def main():
    cfg, uni, sector_map = load_config()
    fallback = uni.get("fallback", "BIL")
    benchmark = uni.get("benchmark", "SPY")
    all_symbols = uni["symbols"]

    client = AlpacaClient()

    print("=" * 60)
    print("Position Monitor  [DRY_RUN — read-only]")
    print("=" * 60)

    account = client.get_account()
    positions = client.get_positions()
    orders = client.get_orders()
    clock = client.get_clock()
    equity = float(account["equity"])

    print(f"\n[account] Market {'OPEN' if clock.get('is_open') else 'CLOSED'}")
    print_account_summary(account)

    # ---- State & risk checks ----
    state = load_state()
    state = update_high_water_mark(state, equity)
    state = update_day_start(state, equity)

    hwm = float(state.get("high_water_mark", equity))
    day_start = float(state.get("day_start_equity", equity))
    dd = (hwm - equity) / hwm if hwm > 0 else 0.0
    dl = (day_start - equity) / day_start if day_start > 0 else 0.0

    print(f"\n[risk] HWM: ${hwm:,.2f}  Day-start: ${day_start:,.2f}")
    for label, check in [("Drawdown", lambda: assert_drawdown_ok(equity, hwm, cfg)),
                          ("Daily loss", lambda: assert_daily_loss_ok(equity, day_start, cfg))]:
        try:
            check()
            val = dd if label == "Drawdown" else dl
            print(f"  {label}: {val:.2%}  OK")
        except Exception as e:
            print(f"  {label}: ALERT — {e}")

    # ---- Per-position stop scan ----
    print("\n[stops] Stop-loss / trailing-stop scan:")
    for pos in positions:
        sym = pos["symbol"]
        price = float(pos.get("current_price", 0))
        avg_entry = float(pos.get("avg_entry_price", 0))
        state = update_trailing_high(state, sym, price)
        peak = get_trailing_high(state, sym)
        sl = is_stop_loss_triggered(price, avg_entry, cfg)
        ts = is_trailing_stop_triggered(price, peak, cfg)
        flag = "  *** STOP-LOSS ***" if sl else ("  *** TRAILING-STOP ***" if ts else "  OK")
        print(f"  {sym:8}  price={price:.2f}  entry={avg_entry:.2f}  peak={peak:.2f}{flag}")
    save_state(state)

    # ---- Positions ----
    print("\n[positions]")
    print_positions(positions, equity)

    open_syms = open_order_symbols(orders)
    if open_syms:
        print(f"\n[orders] Open: {', '.join(sorted(open_syms))}")
    else:
        print("\n[orders] No open orders.")

    # ---- Drift vs target ----
    print("\n[drift] Fetching bars to compute target drift...")
    bars = get_bars_df(client, all_symbols, lookback_days=400)
    check_stale(bars, int(cfg["stale_data_minutes"]))
    equity_syms = [s for s in all_symbols if s != fallback]
    breadth = compute_breadth(bars, equity_syms, int(cfg["trend_lookback"]))
    non_special = [s for s in all_symbols if s not in (fallback, benchmark)]
    signals = compute_signals(bars, cfg, non_special)
    target = build_portfolio(signals, breadth, cfg, sector_map, fallback_symbol=fallback)
    cur = current_weights(positions, equity)
    sells, buys = compute_trades(cur, target, equity, cfg)
    print(f"  Breadth: {breadth:.1%}  Regime: {'RISK-ON' if breadth >= float(cfg['breadth_threshold']) else 'RISK-OFF'}")
    print(f"  Proposed trades (DRY_RUN — not submitted):")
    print_trades(sells, buys)

    state = set_last_run(state, "position_monitor")
    save_state(state)
    print("\n[done] Position monitor complete. No orders submitted.")


if __name__ == "__main__":
    main()
