"""Market data fetching and validation."""
import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import pandas as pd

from src.alpaca_client import AlpacaClient, AlpacaError

# Known feed alternatives for opt-in fallback (ALLOW_DATA_FEED_FALLBACK=true).
_FEED_FALLBACK = {"iex": "sip", "sip": "iex"}

_FEED_ERR_SIGNALS = ("HTTP 403", "HTTP 422", "subscription", "forbidden", "not authorized")


def _is_feed_permission_error(msg: str) -> bool:
    low = msg.lower()
    return any(s.lower() in low for s in _FEED_ERR_SIGNALS)


def get_bars_df(
    client: AlpacaClient,
    symbols: List[str],
    lookback_days: int = 300,
    feed: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch daily bars via Alpaca /v2/stocks/bars.
    Returns DataFrame with MultiIndex (symbol, date) and columns:
    open, high, low, close, volume.

    Feed is resolved from (in order): explicit feed arg → ALPACA_DATA_FEED env → "iex".
    On feed subscription/permission errors, fails closed unless ALLOW_DATA_FEED_FALLBACK=true.
    """
    feed = feed or client.data_feed
    allow_fallback = os.environ.get("ALLOW_DATA_FEED_FALLBACK", "false").lower() == "true"

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    try:
        raw = client.get_bars(symbols, start_str, end_str, feed=feed)
    except AlpacaError as exc:
        msg = str(exc)
        if _is_feed_permission_error(msg):
            fallback = _FEED_FALLBACK.get(feed)
            if allow_fallback and fallback:
                print(
                    f"  [warn] Feed '{feed}' returned a permission/subscription error. "
                    f"Falling back to '{fallback}' (ALLOW_DATA_FEED_FALLBACK=true)."
                )
                raw = client.get_bars(symbols, start_str, end_str, feed=fallback)
            else:
                raise AlpacaError(
                    f"Feed '{feed}' failed with a subscription/permission error and "
                    f"ALLOW_DATA_FEED_FALLBACK=false. "
                    f"Set ALPACA_DATA_FEED to a feed your subscription supports, "
                    f"or set ALLOW_DATA_FEED_FALLBACK=true to enable fallback. "
                    f"Original error: {msg}"
                ) from exc
        else:
            raise
    bars_by_symbol = raw.get("bars", {})

    frames = []
    for sym, bar_list in bars_by_symbol.items():
        if not bar_list:
            continue
        df = pd.DataFrame(bar_list)
        df["symbol"] = sym
        df["date"] = pd.to_datetime(df["t"]).dt.date
        df = df.rename(
            columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        )
        cols = [c for c in ["symbol", "date", "open", "high", "low", "close", "volume"] if c in df.columns]
        frames.append(df[cols].set_index(["symbol", "date"]))

    if not frames:
        return pd.DataFrame(
            columns=["open", "high", "low", "close", "volume"],
            index=pd.MultiIndex.from_tuples([], names=["symbol", "date"]),
        )
    return pd.concat(frames).sort_index()


def bars_to_dict(bars_df: pd.DataFrame) -> dict:
    """Serialize bars DataFrame to a plain dict (for snapshot JSON + hashing)."""
    result = {}
    for sym in bars_df.index.get_level_values("symbol").unique():
        df_sym = bars_df.loc[sym].reset_index()
        df_sym["date"] = df_sym["date"].astype(str)
        result[sym] = df_sym.to_dict(orient="records")
    return result


def latest_bar_age_minutes(bars_df: pd.DataFrame) -> float:
    """Minutes since the most recent bar date (vs today UTC)."""
    if bars_df.empty:
        return float("inf")
    latest_date = max(d for _, d in bars_df.index)
    delta = (datetime.now(timezone.utc).date() - latest_date).days
    return float(delta * 24 * 60)


def check_stale(bars_df: pd.DataFrame, stale_data_minutes: int) -> None:
    """
    Raise AlpacaError if data is too old.
    Allows 3 calendar days for weekend/holiday gaps (Mon = Fri bars = ~3d stale).
    """
    age = latest_bar_age_minutes(bars_df)
    max_minutes = max(float(stale_data_minutes), 3 * 24 * 60)
    if age > max_minutes:
        raise AlpacaError(
            f"Market data is {age / 60:.1f}h old (limit {max_minutes / 60:.1f}h). "
            "Check data feed or market schedule."
        )


def spread_ok(quotes_raw: dict, symbol: str, max_spread_bps: float) -> bool:
    """
    Return True if the bid-ask spread for symbol is within max_spread_bps.
    Returns True (permissive) if quote data is unavailable.
    """
    quotes = quotes_raw.get("quotes", {})
    q = quotes.get(symbol)
    if not q:
        return True
    bid = float(q.get("bp", 0) or 0)
    ask = float(q.get("ap", 0) or 0)
    if bid <= 0 or ask <= 0:
        return True
    mid = (bid + ask) / 2.0
    if mid <= 0:
        return True
    spread_bps = (ask - bid) / mid * 10_000
    return spread_bps <= max_spread_bps
