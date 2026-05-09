#!/usr/bin/env python3
"""
Strategy improvement review: surface IMPROVEMENT-IDEAS.md with current account context.
Read-only. No orders or strategy changes made.

Usage:
  DRY_RUN=true python scripts/run_strategy_improvement_review.py
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
from src.reporting import _pct, _usd
from src.state import load_state, save_state, set_last_run

IMPROVEMENT_IDEAS_PATH = Path(__file__).parent.parent / "memory" / "IMPROVEMENT-IDEAS.md"
IMPROVEMENT_POLICY_PATH = Path(__file__).parent.parent / "config" / "improvement_policy.json"


def main():
    client = AlpacaClient()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    print("=" * 60)
    print("Strategy Improvement Review  [DRY_RUN — read-only]")
    print("=" * 60)

    account = client.get_account()
    equity = float(account["equity"])
    state = load_state()
    hwm = float(state.get("high_water_mark", equity))
    dd = (hwm - equity) / hwm if hwm > 0 else 0.0

    print(f"\n  As of: {now}")
    print(f"  Equity: {_usd(equity)}  |  HWM: {_usd(hwm)}  |  Drawdown: {_pct(dd)}")

    if IMPROVEMENT_POLICY_PATH.exists():
        with open(IMPROVEMENT_POLICY_PATH) as f:
            policy = json.load(f)
        print(f"\n  Policy mode: {policy.get('mode', '?')}")
        print(f"  Paper days before live discussion: {policy.get('min_paper_days_before_live_discussion', 14)}d min / "
              f"{policy.get('preferred_paper_days_before_live_discussion', 30)}d preferred")
        print(f"  Claude may create candidate PRs: {policy.get('claude_may_create_candidate_prs', False)}")
        print(f"  Claude may auto-merge: {policy.get('claude_may_auto_merge_strategy_changes', False)}")

    print(f"\n{'=' * 60}")
    print("Existing improvement ideas:")
    print(f"{'=' * 60}")
    if IMPROVEMENT_IDEAS_PATH.exists():
        content = IMPROVEMENT_IDEAS_PATH.read_text().strip()
        if content:
            print(content[:4000])
            if len(content) > 4000:
                print(f"\n  ... ({len(content) - 4000} more chars — see {IMPROVEMENT_IDEAS_PATH})")
        else:
            print("  (file is empty)")
    else:
        print("  memory/IMPROVEMENT-IDEAS.md not found.")

    print(f"\n{'=' * 60}")
    print("REMINDER: All strategy changes require human approval.")
    print("Claude may propose ideas but may NOT auto-modify config or strategy files.")
    print(f"{'=' * 60}")

    state = set_last_run(state, "strategy_improvement_review")
    save_state(state)
    print("\n[done] Improvement review complete. No changes made.")


if __name__ == "__main__":
    main()
