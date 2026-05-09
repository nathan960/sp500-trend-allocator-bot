from AlgorithmImports import *


class SymbolData:
    def __init__(self, algorithm: QCAlgorithm, symbol: Symbol) -> None:
        self.symbol = symbol

        self.sma200 = algorithm.sma(symbol, 200, Resolution.DAILY)
        self.roc126 = algorithm.roc(symbol, 126, Resolution.DAILY)
        self.roc252 = algorithm.roc(symbol, 252, Resolution.DAILY)
        self.atr20 = algorithm.atr(symbol, 20, MovingAverageType.WILDERS, Resolution.DAILY)

        try:
            algorithm.warm_up_indicator(symbol, self.sma200, Resolution.DAILY)
            algorithm.warm_up_indicator(symbol, self.roc126, Resolution.DAILY)
            algorithm.warm_up_indicator(symbol, self.roc252, Resolution.DAILY)
            algorithm.warm_up_indicator(symbol, self.atr20, Resolution.DAILY)
        except Exception:
            pass

    @property
    def is_ready(self) -> bool:
        return (
            self.sma200.is_ready
            and self.roc126.is_ready
            and self.roc252.is_ready
            and self.atr20.is_ready
        )

    def passes_trend_filter(self, price: float) -> bool:
        if not self.is_ready or price <= 0:
            return False
        return price > float(self.sma200.current.value)

    def momentum_score(self) -> float:
        return 0.5 * float(self.roc126.current.value) + 0.5 * float(self.roc252.current.value)

    def atr_pct(self, price: float) -> float:
        if not self.is_ready or price <= 0:
            return 999.0
        return float(self.atr20.current.value) / price


class Sp500TrendAllocatorV3SectorCaps(QCAlgorithm):
    """
    Version 3: S&P 500 constituent allocator with sector caps,
    updated so live/paper deployment can start trading immediately.

    Core behavior:
        - SPY constituents universe
        - SPY regime filter
        - stock-level trend filter
        - blended 6m / 12m momentum ranking
        - inverse ATR% weighting
        - sector caps
        - BIL fallback in risk-off

    Immediate-start additions:
        - Warm up SPY regime indicators on startup
        - Use daily scheduled rebalance checks after market open
        - Force initial deployment when live/paper starts
        - If constituents are not ready yet:
            * risk-on -> SPY fallback
            * risk-off -> BIL fallback
        - Once stock selection is available, rotate into the intended basket
    """

    def Initialize(self) -> None:
        self.set_start_date(2012, 1, 1)
        self.set_cash(40000)

        try:
            self.settings.seed_initial_prices = True
        except Exception:
            pass

        self.universe_settings.asynchronous = True
        self.universe_settings.resolution = Resolution.DAILY
        self.universe_settings.fill_forward = True
        self.universe_settings.extended_market_hours = False

        # Market regime / benchmark symbols
        # Minute subscription here lets live/paper progress immediately intraday.
        self.spy = self.add_equity("SPY", Resolution.MINUTE).symbol
        self.bil = self.add_equity("BIL", Resolution.MINUTE).symbol
        self.set_benchmark(self.spy)

        self.spy_sma200 = self.sma(self.spy, 200, Resolution.DAILY)
        self.spy_roc126 = self.roc(self.spy, 126, Resolution.DAILY)

        # Warm up regime indicators immediately so deployment doesn't wait.
        try:
            self.warm_up_indicator(self.spy, self.spy_sma200, Resolution.DAILY)
            self.warm_up_indicator(self.spy, self.spy_roc126, Resolution.DAILY)
        except Exception:
            pass

        # Parameters: intentionally still few
        self.max_holdings = self._get_int_parameter("MAX_HOLDINGS", 10)
        self.max_position_weight = self._get_float_parameter("MAX_POSITION_WEIGHT", 0.12)
        self.breadth_threshold = self._get_float_parameter("BREADTH_THRESHOLD", 0.55)
        self.risk_on_equity_alloc = self._get_float_parameter("RISK_ON_EQUITY_ALLOC", 0.90)
        self.min_momentum_6m = self._get_float_parameter("MIN_MOMENTUM_6M", 0.0)
        self.min_momentum_12m = self._get_float_parameter("MIN_MOMENTUM_12M", 0.0)
        self.max_names_per_sector = self._get_int_parameter("MAX_NAMES_PER_SECTOR", 2)

        self.symbol_data = {}
        self.current_constituents = set()

        self.last_rebalance_key = None
        self.last_processed_date = None
        self.initial_deployment_done = False

        # SPY constituents universe
        self.add_universe(
            self.universe.etf(
                "SPY",
                self.universe_settings,
                self._select_constituents
            )
        )

        # Daily check shortly after open so live/paper can deploy immediately.
        self.schedule.on(
            self.date_rules.every_day(self.spy),
            self.time_rules.after_market_open(self.spy, 5),
            self._scheduled_rebalance_check
        )

        self.debug(
            f"[Init] MAX_HOLDINGS={self.max_holdings} "
            f"MAX_POSITION_WEIGHT={self.max_position_weight:.2%} "
            f"BREADTH_THRESHOLD={self.breadth_threshold:.2%} "
            f"RISK_ON_EQUITY_ALLOC={self.risk_on_equity_alloc:.2%} "
            f"MAX_NAMES_PER_SECTOR={self.max_names_per_sector}"
        )

    # -------------------------
    # Parameter helpers
    # -------------------------
    def _get_int_parameter(self, name: str, default: int) -> int:
        getter = getattr(self, "get_parameter", getattr(self, "GetParameter", None))
        if getter is None:
            return default
        try:
            value = getter(name)
            if value is None or str(value) == "":
                return default
            return int(float(value))
        except Exception:
            return default

    def _get_float_parameter(self, name: str, default: float) -> float:
        getter = getattr(self, "get_parameter", getattr(self, "GetParameter", None))
        if getter is None:
            return default
        try:
            value = getter(name)
            if value is None or str(value) == "":
                return default
            return float(value)
        except Exception:
            return default

    # -------------------------
    # Universe
    # -------------------------
    def _select_constituents(self, constituents):
        symbols = []
        updated = set()

        for c in constituents:
            if c.symbol is None:
                continue
            symbols.append(c.symbol)
            updated.add(c.symbol)

        self.current_constituents = updated
        return symbols

    def OnSecuritiesChanged(self, changes: SecurityChanges) -> None:
        for security in changes.added_securities:
            symbol = security.symbol
            if symbol in (self.spy, self.bil):
                continue
            if symbol not in self.symbol_data:
                self.symbol_data[symbol] = SymbolData(self, symbol)

    # -------------------------
    # Main loop
    # -------------------------
    def OnData(self, slice: Slice) -> None:
        if self.is_warming_up:
            return

        current_date = self.time.date()
        if self.last_processed_date == current_date:
            return
        self.last_processed_date = current_date

        # Backup path: if schedule didn't fire for some reason, still evaluate once/day
        self._scheduled_rebalance_check()

    # -------------------------
    # Helpers
    # -------------------------
    def _get_portfolio_holdings_list(self):
        values_attr = getattr(self.portfolio, "Values", None)
        if values_attr is not None:
            try:
                return list(values_attr)
            except Exception:
                pass

        values_fn = getattr(self.portfolio, "values", None)
        if callable(values_fn):
            try:
                return list(values_fn())
            except Exception:
                pass

        holdings = []
        try:
            for item in self.portfolio:
                if hasattr(item, "Value"):
                    holdings.append(item.Value)
                elif isinstance(item, tuple) and len(item) >= 2:
                    holdings.append(item[1])
            if holdings:
                return holdings
        except Exception:
            pass

        return holdings

    def _holding_only_fallback(self) -> bool:
        invested_symbols = []
        for holding in self._get_portfolio_holdings_list():
            sym = getattr(holding, "Symbol", getattr(holding, "symbol", None))
            if not isinstance(sym, Symbol):
                continue
            invested = bool(getattr(holding, "invested", getattr(holding, "Invested", False)))
            if invested:
                invested_symbols.append(sym)

        if len(invested_symbols) == 0:
            return True

        fallback_symbols = {self.spy, self.bil}
        return all(sym in fallback_symbols for sym in invested_symbols)

    def _scheduled_rebalance_check(self) -> None:
        if self.is_warming_up:
            return

        current_date = self.time.date()
        week_key = (self.time.year, self.time.isocalendar()[1])

        force_now = False
        if not self.initial_deployment_done:
            force_now = True
        elif self._holding_only_fallback():
            # Keep checking daily until we transition from fallback into the stock basket.
            force_now = True

        if force_now or self.last_rebalance_key != week_key:
            traded = self._rebalance(force_initial=force_now)
            if traded:
                self.initial_deployment_done = True
                self.last_rebalance_key = week_key

    def _get_sector_code(self, symbol: Symbol):
        """
        Returns Morningstar sector code for a symbol, or None if unavailable.
        """
        try:
            security = self.securities[symbol]
        except Exception:
            return None

        try:
            fundamentals = security.fundamentals
        except Exception:
            return None

        if fundamentals is None:
            return None

        try:
            has_fundamental_data = bool(getattr(fundamentals, "has_fundamental_data", getattr(fundamentals, "HasFundamentalData", False)))
            if not has_fundamental_data:
                return None
        except Exception:
            pass

        try:
            asset_classification = fundamentals.asset_classification
        except Exception:
            try:
                asset_classification = fundamentals.AssetClassification
            except Exception:
                return None

        if asset_classification is None:
            return None

        try:
            sector_code = getattr(
                asset_classification,
                "morningstar_sector_code",
                getattr(asset_classification, "MorningstarSectorCode", None)
            )
            if sector_code is None:
                return None
            return int(sector_code)
        except Exception:
            return None

    # -------------------------
    # Rebalance
    # -------------------------
    def _rebalance(self, force_initial: bool = False) -> bool:
        # Failsafe: if indicators somehow still aren't ready on first live deployment,
        # take a provisional SPY position instead of sitting idle forever.
        if not (self.spy_sma200.is_ready and self.spy_roc126.is_ready):
            if force_initial:
                self.debug("[Rebalance] Regime indicators not ready yet -> provisional SPY allocation")
                self.set_holdings(self.spy, 1.0)
                return True
            return False

        spy_price = float(self.securities[self.spy].price)
        spy_trend_ok = spy_price > float(self.spy_sma200.current.value)
        spy_momentum_ok = float(self.spy_roc126.current.value) > 0.0

        ready_count = 0
        above_count = 0
        candidates = []

        for symbol in list(self.current_constituents):
            if symbol not in self.symbol_data:
                continue
            if symbol not in self.securities:
                continue

            security = self.securities[symbol]
            price = float(security.price)
            if price <= 0 or not security.has_data:
                continue

            sd = self.symbol_data[symbol]
            if not sd.is_ready:
                continue

            ready_count += 1
            if sd.passes_trend_filter(price):
                above_count += 1

            if not sd.passes_trend_filter(price):
                continue

            mom6 = float(sd.roc126.current.value)
            mom12 = float(sd.roc252.current.value)
            if mom6 <= self.min_momentum_6m:
                continue
            if mom12 <= self.min_momentum_12m:
                continue

            sector_code = self._get_sector_code(symbol)
            if sector_code is None:
                continue

            score = sd.momentum_score()
            vol = sd.atr_pct(price)
            candidates.append((symbol, score, vol, sector_code))

        breadth = (above_count / ready_count) if ready_count > 0 else 0.0
        risk_on = spy_trend_ok and spy_momentum_ok and (breadth >= self.breadth_threshold)

        if not risk_on:
            self.debug(
                f"[Rebalance] Risk-off -> BIL | SPY trend={spy_trend_ok} "
                f"SPY mom={spy_momentum_ok} breadth={breadth:.1%}"
            )
            self.set_holdings(self.bil, 1.0)
            return True

        # Rank by momentum first
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Sector cap during selection
        selected = []
        sector_counts = {}

        for symbol, score, vol, sector_code in candidates:
            current_count = sector_counts.get(sector_code, 0)
            if current_count >= self.max_names_per_sector:
                continue

            selected.append((symbol, score, vol, sector_code))
            sector_counts[sector_code] = current_count + 1

            if len(selected) >= self.max_holdings:
                break

        if len(selected) == 0:
            if force_initial:
                self.debug(
                    f"[Rebalance] Risk-on but no eligible names yet -> provisional SPY allocation | breadth={breadth:.1%}"
                )
                self.set_holdings(self.spy, 1.0)
                return True

            self.debug("[Rebalance] Risk-on but no eligible names -> BIL fallback")
            self.set_holdings(self.bil, 1.0)
            return True

        # Inverse-volatility weights using ATR%
        inv_vols = []
        for symbol, score, vol, sector_code in selected:
            safe_vol = max(vol, 0.01)
            inv_vols.append((symbol, 1.0 / safe_vol))

        raw_sum = sum(w for _, w in inv_vols)
        if raw_sum <= 0:
            if force_initial:
                self.set_holdings(self.spy, 1.0)
                return True
            self.set_holdings(self.bil, 1.0)
            return True

        uncapped_weights = {
            symbol: (inv_w / raw_sum) * self.risk_on_equity_alloc
            for symbol, inv_w in inv_vols
        }

        # Cap position weights, then send any leftover to BIL
        final_weights = {}
        stock_weight_sum = 0.0
        for symbol, w in uncapped_weights.items():
            capped = min(w, self.max_position_weight)
            final_weights[symbol] = capped
            stock_weight_sum += capped

        residual = max(0.0, 1.0 - stock_weight_sum)

        targets = [PortfolioTarget(symbol, weight) for symbol, weight in final_weights.items()]
        targets.append(PortfolioTarget(self.bil, residual))

        self.set_holdings(targets, liquidate_existing_holdings=True)

        preview = ", ".join([f"{symbol.value}:{weight:.2%}" for symbol, weight in list(final_weights.items())[:10]])
        sector_preview = ", ".join([f"{sector}:{count}" for sector, count in sorted(sector_counts.items(), key=lambda x: x[0])])

        self.debug(
            f"[Rebalance] Risk-on | breadth={breadth:.1%} | selected={len(final_weights)} "
            f"| stock_alloc={stock_weight_sum:.2%} | bil={residual:.2%} "
            f"| sector_counts={sector_preview} | {preview}"
        )
        return True