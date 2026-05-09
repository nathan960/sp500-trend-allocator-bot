"""
Alpaca REST client.
Default base URL is paper-api to prevent accidental live trading.
All write methods are blocked when DRY_RUN=true (the default).
"""
import os
import requests

PAPER_BASE_URL = "https://paper-api.alpaca.markets"
PAPER_DATA_URL = "https://data.alpaca.markets"


class AlpacaError(Exception):
    pass


class AlpacaClient:
    def __init__(self):
        self.api_key = os.environ["ALPACA_API_KEY"]
        self.secret_key = os.environ["ALPACA_SECRET_KEY"]
        self.base_url = os.environ.get("ALPACA_BASE_URL", PAPER_BASE_URL).rstrip("/")
        self.data_url = os.environ.get("ALPACA_DATA_URL", PAPER_DATA_URL).rstrip("/")
        self.dry_run = os.environ.get("DRY_RUN", "true").lower() == "true"
        self.trading_mode = os.environ.get("TRADING_MODE", "paper").lower()
        self.live_confirmed = (
            os.environ.get("LIVE_TRADING_CONFIRMED", "false").lower() == "true"
        )
        if self.trading_mode == "live" and not self.live_confirmed:
            raise AlpacaError(
                "TRADING_MODE=live requires LIVE_TRADING_CONFIRMED=true. "
                "Set LIVE_TRADING_CONFIRMED=true only after reviewing all risks."
            )

    @property
    def is_dry_run(self) -> bool:
        return self.dry_run

    def _headers(self) -> dict:
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
        }

    def _get(self, endpoint: str, params: dict = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        r = requests.get(url, headers=self._headers(), params=params, timeout=15)
        r.raise_for_status()
        return r.json()

    def _data_get(self, endpoint: str, params: dict = None):
        url = f"{self.data_url}{endpoint}"
        r = requests.get(url, headers=self._headers(), params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint: str, payload: dict) -> dict:
        if self.dry_run:
            raise AlpacaError(
                f"DRY_RUN=true: blocked POST {endpoint} payload={payload}"
            )
        url = f"{self.base_url}{endpoint}"
        r = requests.post(url, headers=self._headers(), json=payload, timeout=15)
        r.raise_for_status()
        return r.json()

    def _delete(self, endpoint: str) -> int:
        if self.dry_run:
            raise AlpacaError(f"DRY_RUN=true: blocked DELETE {endpoint}")
        url = f"{self.base_url}{endpoint}"
        r = requests.delete(url, headers=self._headers(), timeout=15)
        if r.status_code not in (200, 204, 207):
            r.raise_for_status()
        return r.status_code

    # ---- Read-only ----

    def get_account(self) -> dict:
        return self._get("/v2/account")

    def get_positions(self) -> list:
        return self._get("/v2/positions")

    def get_orders(self, status: str = "open") -> list:
        return self._get("/v2/orders", params={"status": status, "limit": 500})

    def get_clock(self) -> dict:
        return self._get("/v2/clock")

    def get_bars(
        self,
        symbols: list,
        start: str,
        end: str,
        timeframe: str = "1Day",
        feed: str = "iex",
    ) -> dict:
        """Multi-symbol daily bars from /v2/stocks/bars."""
        params = {
            "symbols": ",".join(symbols),
            "start": start,
            "end": end,
            "timeframe": timeframe,
            "feed": feed,
            "limit": 10000,
        }
        return self._data_get("/v2/stocks/bars", params=params)

    def get_latest_quotes(self, symbols: list, feed: str = "iex") -> dict:
        """Latest NBBO quotes from /v2/stocks/quotes/latest (for spread checks)."""
        params = {
            "symbols": ",".join(symbols),
            "feed": feed,
        }
        return self._data_get("/v2/stocks/quotes/latest", params=params)

    # ---- Write (blocked by DRY_RUN) ----

    def submit_buy_notional(
        self, symbol: str, notional: float, time_in_force: str = "day"
    ) -> dict:
        """Market buy by notional dollar amount."""
        return self._post(
            "/v2/orders",
            {
                "symbol": symbol,
                "notional": round(float(notional), 2),
                "side": "buy",
                "type": "market",
                "time_in_force": time_in_force,
            },
        )

    def submit_sell_qty(
        self, symbol: str, qty: float, time_in_force: str = "day"
    ) -> dict:
        """Market sell by share quantity."""
        return self._post(
            "/v2/orders",
            {
                "symbol": symbol,
                "qty": str(round(float(qty), 6)),
                "side": "sell",
                "type": "market",
                "time_in_force": time_in_force,
            },
        )

    def cancel_all_orders(self) -> int:
        """Cancel all open orders."""
        return self._delete("/v2/orders")
