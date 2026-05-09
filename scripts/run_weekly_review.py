#!/usr/bin/env python3
"""
Weekly review: account snapshot + week P&L → memory/WEEKLY-REVIEW.md.
Read-only. No orders submitted.

Usage:
  DRY_RUN=true python scripts/run_weekly_review.py
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

os.environ["DRY_RUN"] = "true"

from src.alpaca_client import AlpacaClient
from src.reporting import WEEKLY_REVIEW_PATH, _pct, _usd
from src.state import load_state, save_state, set_last_run


def main():
    client = AlpacaClient()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    print("=" * 60)
    print("Weekly Review  [DRY_RUN — read-only]")
    print("=" * 60)

    account = client.get_account()
    positions = client.get_positions()
    equity = float(account["equity"])
    cash = float(account["cash"])

    state = load_state()
    hwm = float(state.get("high_water_mark", equity))
    dd = (hwm - equity) / hwm if hwm > 0 else 0.0
    last_weekly = state.get("last_run_weekly_review", "never")

    today = datetime.now(timezone.utc)
    if today.weekday() == 0 or "week_start_equity" not in state:
        state["week_start_equity"] = equity
        state["week_start_date"] = today.date().isoformat()

    week_start = float(state.get("week_start_equity", equity))
    week_pl = equity - week_start
    week_ret = week_pl / week_start if week_start > 0 else 0.0

    print(f"\n  Equity:          {_usd(equity)}")
    print(f"  Cash:            {_usd(cash)}")
    print(f"  Week P&L:        {_usd(week_pl)}  ({_pct(week_ret)})")
    print(f"  Drawdown/HWM:    {_pct(dd)}")
    print(f"  Last weekly run: {last_weekly}")

    print("\n  Positions:")
    for p in sorted(positions, key=lambda x: float(x.get("market_value", 0)), reverse=True):
        mv = float(p.get("market_value", 0))
        w = mv / equity if equity > 0 else 0.0
        pl = float(p.get("unrealized_pl", 0))
        print(f"    {p['symbol']:8} {_pct(w)}  {_usd(mv)}  unr {_usd(pl)}")

    section = f"""
## Weekly Review — {now}

- Equity: {_usd(equity)}
- Cash: {_usd(cash)}
- Week P&L: {_usd(week_pl)} ({_pct(week_ret)})
- Drawdown from HWM ({_usd(hwm)}): {_pct(dd)}
- Previous weekly run: {last_weekly}

### Positions
"""
    for p in sorted(positions, key=lambda x: float(x.get("market_value", 0)), reverse=True):
        mv = float(p.get("market_value", 0))
        w = mv / equity if equity > 0 else 0.0
        pl = float(p.get("unrealized_pl", 0))
        section += f"- {p['symbol']}: {_pct(w)} ({_usd(mv)}, unr {_usd(pl)})\n"

    WEEKLY_REVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = WEEKLY_REVIEW_PATH.read_text() if WEEKLY_REVIEW_PATH.exists() else ""
    WEEKLY_REVIEW_PATH.write_text(existing.rstrip() + "\n" + section)
    print(f"\n  Appended to {WEEKLY_REVIEW_PATH}")

    state = set_last_run(state, "weekly_review")
    save_state(state)
    print("\n[done] Weekly review complete.")


if __name__ == "__main__":
    main()
