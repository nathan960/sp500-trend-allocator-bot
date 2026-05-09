#!/usr/bin/env python3
"""
Stage 1: Market Data + Signal Plan.

Fetches Alpaca market data and account state, computes deterministic strategy
signals, and writes:
  data/latest/market_snapshot.json
  data/latest/trade_plan.json
  memory/SIGNAL-LOG.md  (appended)
  memory/DATA-LOG.md    (appended)

THIS SCRIPT NEVER PLACES ORDERS.
DRY_RUN is forced to 'true' at startup — the write API is never called here.
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Stage 1 is structurally incapable of placing orders.
# Force DRY_RUN regardless of environment to be explicit.
os.environ["DRY_RUN"] = "true"

from src.alpaca_client import AlpacaClient
from src.data import bars_to_dict, check_stale, get_bars_df, latest_bar_age_minutes
from src.plan import write_plan, write_snapshot
from src.reporting import append_data_log, append_signal_log, print_signals, print_target_weights
from src.strategy import build_portfolio, compute_breadth, compute_signals


def load_config():
    root = Path(__file__).parent.parent
    with open(root / "config" / "strategy.json") as f:
        raw = json.load(f)
    cfg = raw["parameters"]
    cfg["strategy_version"] = raw.get("strategy_version", "2.0")
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
    # Symbols to score (exclude benchmark from signal ranking; include fallback for data)
    scoreable = [s for s in all_symbols if s not in (benchmark,)]
    equity_symbols = [s for s in all_symbols if s not in (fallback,)]

    client = AlpacaClient()

    print("=" * 60)
    print("Stage 1: Market Data + Signal Plan  [NO ORDERS]")
    print("=" * 60)
    print(f"Universe: {len(all_symbols)} symbols  |  fallback={fallback}  benchmark={benchmark}")

    # ---- Fetch account state (read-only) ----
    print("\n[account] Fetching account, positions, orders, clock...")
    account = client.get_account()
    positions = client.get_positions()
    orders = client.get_orders()
    clock = client.get_clock()
    equity = float(account["equity"])
    market_open = clock.get("is_open", False)
    print(f"  Equity: ${equity:,.2f}  |  Market: {'OPEN' if market_open else 'CLOSED'}")

    # ---- Fetch market data ----
    print("\n[data] Fetching daily bars (300d lookback)...")
    bars = get_bars_df(client, all_symbols, lookback_days=400)
    n_syms = bars.index.get_level_values("symbol").nunique()
    print(f"  Received bars for {n_syms}/{len(all_symbols)} symbols")
    check_stale(bars, int(cfg["stale_data_minutes"]))
    age_h = latest_bar_age_minutes(bars) / 60
    print(f"  Data age: {age_h:.1f}h")

    # ---- Fetch latest quotes (for spread info in snapshot) ----
    print("\n[quotes] Fetching latest quotes...")
    try:
        quotes_raw = client.get_latest_quotes(all_symbols)
        print(f"  Received quotes for {len(quotes_raw.get('quotes', {}))} symbols")
    except Exception as e:
        print(f"  [warn] Quote fetch failed: {e} — spread check disabled")
        quotes_raw = {}

    # ---- Write market snapshot ----
    bars_dict = bars_to_dict(bars)
    snapshot = {
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "bars": bars_dict,
        "quotes": quotes_raw,
        "account": account,
        "positions": positions,
        "open_orders": orders,
        "clock": clock,
    }
    write_snapshot(snapshot)
    print("\n[snapshot] Written: data/latest/market_snapshot.json")

    # ---- Compute signals ----
    print("\n[signals] Computing trend/momentum signals...")
    non_special = [s for s in scoreable if s not in (fallback,)]
    signals = compute_signals(bars, cfg, non_special)
    eligible_count = int(signals["eligible"].sum()) if not signals.empty else 0

    breadth = compute_breadth(bars, equity_symbols, int(cfg["trend_lookback"]))
    regime = "risk_on" if breadth >= float(cfg["breadth_threshold"]) else "risk_off"
    print(f"  Breadth: {breadth:.1%}  Threshold: {cfg['breadth_threshold']:.0%}  → {regime.upper()}")
    print(f"  Eligible: {eligible_count}/{len(signals)} symbols scored")

    # ---- Build portfolio ----
    target = build_portfolio(signals, breadth, cfg, sector_map, fallback_symbol=fallback)
    print("\n[target] Target Weights:")
    print_target_weights(target)

    if not signals.empty:
        print("\n[signals] Per-symbol table:")
        print_signals(signals, target)

    # ---- Write trade plan ----
    plan = write_plan(target, breadth, regime, bars_dict, cfg)
    print(f"\n[plan] Written: data/latest/trade_plan.json")
    print(f"  Data hash: {plan['data_hash']}  |  Expires in: {plan['plan_max_age_minutes']}min")

    # ---- Append memory logs ----
    append_signal_log(plan, signals, eligible_count)
    append_data_log({
        "n_symbols": n_syms,
        "bars_age_h": round(age_h, 1),
        "market_open": market_open,
        "equity": equity,
        "data_hash": plan["data_hash"],
    })
    print("\n[log] Appended memory/SIGNAL-LOG.md and memory/DATA-LOG.md")

    print("\n[done] Stage 1 complete. No orders were placed.")
    print("       Run scripts/run_trade_execution.py to execute the plan.")


if __name__ == "__main__":
    main()
