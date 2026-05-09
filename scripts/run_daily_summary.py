#!/usr/bin/env python3
"""
Daily summary: account snapshot + target weights → memory/DAILY-SUMMARY.md.
Read-only. No orders submitted.

Usage:
  DRY_RUN=true python scripts/run_daily_summary.py
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
from src.reporting import (
    print_account_summary,
    print_positions,
    print_target_weights,
    write_daily_summary,
)
from src.state import (
    load_state,
    save_state,
    set_last_run,
    update_day_start,
    update_high_water_mark,
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
    print("Daily Summary  [DRY_RUN — read-only]")
    print("=" * 60)

    account = client.get_account()
    positions = client.get_positions()
    equity = float(account["equity"])

    print("\n[account]")
    print_account_summary(account)
    print("\n[positions]")
    print_positions(positions, equity)

    state = load_state()
    state = update_high_water_mark(state, equity)
    state = update_day_start(state, equity)

    hwm = float(state.get("high_water_mark", equity))
    dd = (hwm - equity) / hwm if hwm > 0 else 0.0
    print(f"\n[risk] HWM: ${hwm:,.2f}  Drawdown: {dd:.2%}")

    print("\n[signals] Computing target weights...")
    bars = get_bars_df(client, all_symbols, lookback_days=400)
    check_stale(bars, int(cfg["stale_data_minutes"]))
    equity_syms = [s for s in all_symbols if s != fallback]
    breadth = compute_breadth(bars, equity_syms, int(cfg["trend_lookback"]))
    non_special = [s for s in all_symbols if s not in (fallback, benchmark)]
    signals = compute_signals(bars, cfg, non_special)
    target = build_portfolio(signals, breadth, cfg, sector_map, fallback_symbol=fallback)

    regime = "RISK-ON" if breadth >= float(cfg["breadth_threshold"]) else "RISK-OFF"
    print(f"  Breadth: {breadth:.1%}  → {regime}")
    print("\n[target]")
    print_target_weights(target)

    print("\n[write] Saving to memory/DAILY-SUMMARY.md...")
    write_daily_summary(account, positions, target, state)

    state = set_last_run(state, "daily_summary")
    save_state(state)
    print("\n[done] Daily summary complete.")


if __name__ == "__main__":
    main()
