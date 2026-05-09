#!/usr/bin/env python3
"""
Signal check: compute target portfolio weights and show proposed trades.
Always enforces DRY_RUN=true — this script never submits orders.

Usage:
  DRY_RUN=true python scripts/run_signal_check.py
  DRY_RUN=true python scripts/run_signal_check.py --trades   # show trade list too
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Allow importing src/ from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Enforce read-only regardless of environment
os.environ["DRY_RUN"] = "true"

from src.alpaca_client import AlpacaClient
from src.data import check_stale, get_bars_df
from src.execution import compute_trades, current_weights
from src.reporting import print_signals, print_target_weights, print_trades
from src.state import load_state
from src.strategy import build_portfolio, compute_breadth, compute_signals


def load_config():
    root = Path(__file__).parent.parent
    with open(root / "config" / "strategy.json") as f:
        raw = json.load(f)
    cfg = raw["parameters"]
    with open(root / "config" / "universe.json") as f:
        universe_cfg = json.load(f)
    with open(root / "config" / "sector_map.json") as f:
        sector_map = json.load(f)
    return cfg, universe_cfg, sector_map


def main():
    parser = argparse.ArgumentParser(description="Compute target portfolio weights (read-only).")
    parser.add_argument("--trades", action="store_true", help="Also show proposed trade list.")
    parser.add_argument("--verbose", action="store_true", help="Show per-symbol signal table.")
    args = parser.parse_args()

    cfg, universe_cfg, sector_map = load_config()
    fallback = universe_cfg.get("fallback", "BIL")
    benchmark = universe_cfg.get("benchmark", "SPY")
    all_symbols = universe_cfg["symbols"]
    tradeable = [s for s in all_symbols if s not in (benchmark,)]
    equity_symbols = [s for s in all_symbols if s not in (fallback,)]

    client = AlpacaClient()

    print("=" * 60)
    print("Signal Check  [DRY_RUN — no orders]")
    print("=" * 60)
    print(f"Universe: {len(all_symbols)} symbols  |  Fallback: {fallback}  |  Benchmark: {benchmark}")

    # ---- Market data ----
    print("\n[data] Fetching bars (lookback 300d)...")
    bars = get_bars_df(client, all_symbols, lookback_days=400)
    n_syms = bars.index.get_level_values("symbol").nunique()
    print(f"[data] Received bars for {n_syms}/{len(all_symbols)} symbols")
    check_stale(bars, int(cfg["stale_data_minutes"]))

    # ---- Regime ----
    breadth = compute_breadth(bars, equity_symbols, int(cfg["trend_lookback"]))
    regime = "RISK-ON" if breadth >= float(cfg["breadth_threshold"]) else "RISK-OFF"
    print(f"\n[regime] Breadth: {breadth:.1%}  Threshold: {cfg['breadth_threshold']:.1%}  → {regime}")

    # ---- Signals ----
    non_special = [s for s in all_symbols if s not in (fallback, benchmark)]
    signals = compute_signals(bars, cfg, non_special)
    eligible_count = int(signals["eligible"].sum()) if not signals.empty else 0
    print(f"[signals] {eligible_count} eligible / {len(signals)} scored")

    if args.verbose and not signals.empty:
        print("\n[signals] Per-symbol signal table:")
        target_preview = build_portfolio(signals, breadth, cfg, sector_map, fallback_symbol=fallback)
        print_signals(signals, target_preview)

    # ---- Target weights ----
    target = build_portfolio(signals, breadth, cfg, sector_map, fallback_symbol=fallback)
    print("\n[target] Target Weights:")
    print_target_weights(target)

    # ---- Trade list (read-only; DRY_RUN guaranteed) ----
    if args.trades:
        account = client.get_account()
        positions = client.get_positions()
        equity = float(account["equity"])
        cur = current_weights(positions, equity)
        sells, buys = compute_trades(cur, target, equity, cfg)
        print(f"\n[trades] Proposed trades (DRY_RUN — not submitted):")
        print_trades(sells, buys)

    print("\n[done] Signal check complete. No orders were submitted.")


if __name__ == "__main__":
    main()
