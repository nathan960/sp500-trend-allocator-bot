"""
Two-stage trade plan handoff.

Stage 1 (run_market_data_update.py) calls write_plan() + write_snapshot().
Stage 2 (run_trade_execution.py) calls read_plan(), then verifies before any orders.

The plan file lives at data/latest/trade_plan.json and is gitignored.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
PLAN_PATH = ROOT / "data" / "latest" / "trade_plan.json"
SNAPSHOT_PATH = ROOT / "data" / "latest" / "market_snapshot.json"

DEFAULT_MAX_AGE_MINUTES = 90


class PlanError(Exception):
    """Raised when the trade plan cannot be verified for execution."""


def _bars_hash(bars_dict: dict) -> str:
    """Stable 16-char SHA-256 prefix of the serialized bars payload."""
    payload = json.dumps(bars_dict, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def write_plan(
    target_weights: dict,
    breadth: float,
    regime: str,
    bars_dict: dict,
    cfg: dict,
) -> dict:
    """
    Write data/latest/trade_plan.json and return the plan dict.
    Called only from Stage 1 (no order submission capability there).
    """
    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_max_age_minutes": DEFAULT_MAX_AGE_MINUTES,
        "strategy_version": str(cfg.get("strategy_version", "2.0")),
        "regime": regime,
        "breadth": round(float(breadth), 6),
        "target_weights": {k: round(float(v), 6) for k, v in sorted(target_weights.items())},
        "data_hash": _bars_hash(bars_dict),
        "approved": True,
    }
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLAN_PATH.write_text(json.dumps(plan, indent=2))
    return plan


def write_snapshot(snapshot: dict) -> None:
    """Write data/latest/market_snapshot.json (raw market data + account state)."""
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, default=str))


def read_plan() -> dict:
    """Load trade_plan.json. Raises PlanError if the file does not exist."""
    if not PLAN_PATH.exists():
        raise PlanError(
            f"Trade plan not found: {PLAN_PATH}. "
            "Run scripts/run_market_data_update.py first."
        )
    with open(PLAN_PATH) as f:
        return json.load(f)


def verify_freshness(plan: dict) -> None:
    """Raise PlanError if the plan is older than plan_max_age_minutes."""
    gen_str = plan.get("generated_at")
    if not gen_str:
        raise PlanError("Plan is missing generated_at timestamp.")
    gen_dt = datetime.fromisoformat(gen_str)
    if gen_dt.tzinfo is None:
        gen_dt = gen_dt.replace(tzinfo=timezone.utc)
    age_min = (datetime.now(timezone.utc) - gen_dt).total_seconds() / 60.0
    max_age = float(plan.get("plan_max_age_minutes", DEFAULT_MAX_AGE_MINUTES))
    if age_min > max_age:
        raise PlanError(
            f"Trade plan is {age_min:.1f} min old (limit: {max_age:.0f} min). "
            "Re-run run_market_data_update.py to generate a fresh plan."
        )


def verify_approved(plan: dict) -> None:
    """Raise PlanError if approved=false."""
    if not plan.get("approved", False):
        raise PlanError(
            "Trade plan has approved=false. "
            "Set approved=true in data/latest/trade_plan.json after review."
        )


def verify_data_hash(plan: dict, bars_dict: dict) -> None:
    """
    Raise PlanError if the bars hash does not match.
    Pass an empty dict to skip (Stage 2 does not re-fetch bars).
    """
    if not bars_dict:
        return
    expected = plan.get("data_hash", "")
    actual = _bars_hash(bars_dict)
    if expected and expected != actual:
        raise PlanError(
            f"Data hash mismatch — plan: {expected}, recomputed: {actual}. "
            "Re-run run_market_data_update.py."
        )
