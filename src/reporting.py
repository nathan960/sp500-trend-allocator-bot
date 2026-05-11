"""Console reporting and memory file appending."""
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT = Path(__file__).parent.parent
DAILY_SUMMARY_PATH = ROOT / "memory" / "DAILY-SUMMARY.md"
WEEKLY_REVIEW_PATH = ROOT / "memory" / "WEEKLY-REVIEW.md"
SIGNAL_LOG_PATH = ROOT / "memory" / "SIGNAL-LOG.md"
TRADE_LOG_PATH = ROOT / "memory" / "TRADE-LOG.md"
DATA_LOG_PATH = ROOT / "memory" / "DATA-LOG.md"


def _pct(v) -> str:
    return f"{float(v):.2%}" if v is not None else "N/A"


def _usd(v) -> str:
    return f"${float(v):,.2f}" if v is not None else "N/A"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text() if path.exists() else ""
    path.write_text(existing.rstrip() + "\n\n" + text.strip() + "\n")


# ---------------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------------

def print_account_summary(account: dict) -> None:
    equity = float(account.get("equity", 0))
    cash = float(account.get("cash", 0))
    bp = float(account.get("buying_power", 0))
    last = float(account.get("last_equity", equity))
    print(f"  Equity:        {_usd(equity)}")
    print(f"  Cash:          {_usd(cash)}")
    print(f"  Buying power:  {_usd(bp)}")
    print(f"  Day P&L est:   {_usd(equity - last)}")


def print_positions(positions: list, equity: float) -> None:
    if not positions:
        print("  (no open positions)")
        return
    print(f"  {'Symbol':8} {'Qty':>10} {'Price':>10} {'Mkt Value':>12} {'Weight':>8} {'Unr P&L':>10}")
    print(f"  {'-'*62}")
    for p in sorted(positions, key=lambda x: float(x.get("market_value", 0)), reverse=True):
        mv = float(p.get("market_value", 0))
        price = float(p.get("current_price", 0))
        qty = float(p.get("qty", 0))
        w = mv / equity if equity > 0 else 0.0
        pl = float(p.get("unrealized_pl", 0))
        print(f"  {p['symbol']:8} {qty:>10.4f} {_usd(price):>10} {_usd(mv):>12} {_pct(w):>8} {_usd(pl):>10}")


def print_signals(signals_df: pd.DataFrame, target_weights: dict) -> None:
    hdr = f"  {'Symbol':8} {'Score':>8} {'MomFast':>8} {'MomSlow':>8} {'AbvSMA':>7} {'ATR%':>6} {'Target':>8} {'OK':>4}"
    print(hdr)
    print(f"  {'-'*len(hdr.rstrip())}")
    for sym, row in signals_df.sort_values("score", ascending=False).iterrows():
        mf = row["momentum_fast"] if row["momentum_fast"] is not None else float("nan")
        ms = row["momentum_slow"] if row["momentum_slow"] is not None else float("nan")
        atr = row["atr_pct"] * 100 if row["atr_pct"] < float("inf") else float("nan")
        print(
            f"  {sym:8} {row['score']:>8.4f} {mf:>8.4f} {ms:>8.4f} "
            f"{'Y' if row['above_trend_sma'] else 'N':>7} "
            f"{atr:>5.2f}% {_pct(target_weights.get(sym, 0)):>8} "
            f"{'Y' if row['eligible'] else 'N':>4}"
        )


def print_target_weights(target_weights: dict) -> None:
    if not target_weights:
        print("  (all cash)")
        return
    print(f"  {'Symbol':8} {'Weight':>10}")
    print(f"  {'-'*20}")
    for sym, w in sorted(target_weights.items(), key=lambda x: -x[1]):
        print(f"  {sym:8} {_pct(w):>10}")
    total = sum(target_weights.values())
    print(f"  {'-'*20}")
    print(f"  {'TOTAL':8} {_pct(total):>10}")
    print(f"  {'CASH':8} {_pct(max(0, 1.0 - total)):>10}")


def print_trades(sells: list, buys: list) -> None:
    all_trades = sells + buys
    if not all_trades:
        print("  No trades needed (all within rebalance threshold).")
        return
    print(f"  {'Side':5} {'Symbol':8} {'Notional':>12} {'Cur%':>7} {'Tgt%':>7}")
    print(f"  {'-'*44}")
    for t in all_trades:
        print(
            f"  {t['side'].upper():5} {t['symbol']:8} "
            f"{_usd(t['notional']):>12} "
            f"{_pct(t['current_weight']):>7} "
            f"{_pct(t['target_weight']):>7}"
        )


# ---------------------------------------------------------------------------
# Memory file writers
# ---------------------------------------------------------------------------

def write_daily_summary(
    account: dict,
    positions: list,
    target_weights: dict,
    state: dict,
    as_of: str = None,
) -> None:
    """Overwrite memory/DAILY-SUMMARY.md."""
    as_of = as_of or date.today().isoformat()
    equity = float(account.get("equity", 0))
    cash = float(account.get("cash", 0))
    last = float(account.get("last_equity", equity))
    hwm = float(state.get("high_water_mark", equity))
    dd = (hwm - equity) / hwm if hwm > 0 else 0.0

    lines = [
        f"# Daily Summary — {as_of}",
        "",
        f"- Equity: {_usd(equity)}",
        f"- Cash: {_usd(cash)}",
        f"- Day P&L (vs last_equity): {_usd(equity - last)}",
        f"- Drawdown from HWM: {_pct(dd)}",
        "",
        "## Target Weights",
        "",
    ]
    if not target_weights:
        lines.append("- (all cash)")
    else:
        for sym, w in sorted(target_weights.items(), key=lambda x: -x[1]):
            lines.append(f"- {sym}: {_pct(w)}")
        lines.append(f"- Cash: {_pct(max(0, 1.0 - sum(target_weights.values())))}")
    lines += ["", "## Positions", ""]
    if not positions:
        lines.append("- (none)")
    else:
        for p in sorted(positions, key=lambda x: float(x.get("market_value", 0)), reverse=True):
            mv = float(p.get("market_value", 0))
            w = mv / equity if equity > 0 else 0.0
            pl = float(p.get("unrealized_pl", 0))
            lines.append(f"- {p['symbol']}: {_pct(w)} ({_usd(mv)}, unr P&L {_usd(pl)})")
    lines.append("")
    DAILY_SUMMARY_PATH.write_text("\n".join(lines))
    print(f"  Written: {DAILY_SUMMARY_PATH}")


def append_signal_log(
    plan: dict,
    signals_df: pd.DataFrame,
    eligible_count: int,
) -> None:
    """Append a signal entry to memory/SIGNAL-LOG.md."""
    now = _now_iso()
    target = plan.get("target_weights", {})
    total_w = sum(target.values())
    lines = [
        f"## {now} — Signal Check",
        "",
        f"- Regime: {plan.get('regime', '?').upper()}",
        f"- Breadth: {plan.get('breadth', 0):.1%}",
        f"- Eligible: {eligible_count}/{len(signals_df)} scored",
        f"- Data hash: {plan.get('data_hash', '?')}",
        "",
        "**Target weights:**",
        "",
    ]
    if not target:
        lines.append("- (all cash)")
    else:
        for sym, w in sorted(target.items(), key=lambda x: -x[1]):
            lines.append(f"- {sym}: {_pct(w)}")
        lines.append(f"- Cash: {_pct(max(0, 1.0 - total_w))}")
    _append(SIGNAL_LOG_PATH, "\n".join(lines))


def append_trade_log(
    results: List[dict],
    plan: dict,
    equity: float,
    dry_run: bool,
) -> None:
    """Append an execution entry to memory/TRADE-LOG.md."""
    now = _now_iso()
    mode = "DRY_RUN" if dry_run else "LIVE_PAPER"
    submitted = [r for r in results if r.get("status") == "submitted"]
    dry_results = [r for r in results if r.get("status") == "dry_run"]
    skipped = [r for r in results if r.get("status", "").startswith("skipped")]
    errors = [r for r in results if r.get("status", "").startswith("error")]

    lines = [
        f"## {now} — Trade Execution [{mode}]",
        "",
        f"- Regime: {plan.get('regime', '?').upper()}",
        f"- Plan age at execution: see trade_plan.json generated_at",
        f"- Pre-execution equity: {_usd(equity)}",
        f"- Orders submitted: {len(submitted)}  dry-run: {len(dry_results)}  skipped: {len(skipped)}  errors: {len(errors)}",
        "",
        "**Orders:**",
        "",
    ]
    for r in results:
        sym = r.get("symbol", "?")
        side = r.get("side", "?").upper()
        notional = r.get("notional", 0)
        qty = r.get("qty", "")
        status = r.get("status", "?")
        qty_str = f" qty={qty}" if qty else f" notional={_usd(notional)}"
        lines.append(f"- {side} {sym}{qty_str} [{status}]")

    _append(TRADE_LOG_PATH, "\n".join(lines))


def append_data_log(snapshot_summary: dict) -> None:
    """Append a data fetch entry to memory/DATA-LOG.md."""
    now = _now_iso()
    lines = [
        f"## {now} — Market Data Update",
        "",
        f"- Symbols fetched: {snapshot_summary.get('n_symbols', '?')}",
        f"- Bars age: {snapshot_summary.get('bars_age_h', '?')}h",
        f"- Market: {'OPEN' if snapshot_summary.get('market_open') else 'CLOSED'}",
        f"- Account equity: {_usd(snapshot_summary.get('equity', 0))}",
        f"- Data hash: {snapshot_summary.get('data_hash', '?')}",
        f"- Data feed: {snapshot_summary.get('data_feed', '?')}",
    ]
    _append(DATA_LOG_PATH, "\n".join(lines))
