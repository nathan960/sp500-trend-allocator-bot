"""Persistent strategy state via memory/RISK-STATE.json."""
import json
from datetime import date, datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).parent.parent / "memory" / "RISK-STATE.json"


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)


def update_high_water_mark(state: dict, equity: float) -> dict:
    hwm = float(state.get("high_water_mark", 0.0))
    if equity > hwm:
        state["high_water_mark"] = equity
        state["high_water_mark_date"] = date.today().isoformat()
    return state


def update_day_start(state: dict, equity: float) -> dict:
    """Record start-of-day equity once per calendar day."""
    today = date.today().isoformat()
    if state.get("day_start_date") != today:
        state["day_start_equity"] = equity
        state["day_start_date"] = today
    return state


def get_trailing_high(state: dict, symbol: str) -> float:
    return float(state.get("trailing_highs", {}).get(symbol, 0.0))


def update_trailing_high(state: dict, symbol: str, price: float) -> dict:
    highs = state.setdefault("trailing_highs", {})
    if price > float(highs.get(symbol, 0.0)):
        highs[symbol] = price
    return state


def set_last_run(state: dict, script: str) -> dict:
    state[f"last_run_{script}"] = datetime.now(timezone.utc).isoformat()
    return state
