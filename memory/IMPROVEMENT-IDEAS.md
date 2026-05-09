# Improvement Ideas

Claude may propose improvements only. Human approval required.

---

## Review 2026-05-09

### Paper data status

INSUFFICIENT PAPER DATA — WEEKLY-REVIEW.md contains no paper trading entries. Fewer than 14 days of live/paper data exist. Backtest-only analysis follows.

### Observations

- **PSR = 14%**: Critically low. A PSR of 14% means there is only a ~14% probability the true Sharpe exceeds a zero benchmark, given observed return variance. This is the most serious statistical red flag in the backtest.
- **Max drawdown = 34.9%**: High for a trend-following strategy whose primary defense mechanism is the SPY 200-day SMA and breadth filter. Suggests the regime filter is slow to exit risk-on during bear transitions.
- **Drawdown recovery = 986 days (~2.7 years)**: Extremely long. Implies the strategy can be underwater for nearly three years after a peak, which may cause live abandonment before recovery.
- **Sharpe = 0.7, Sortino = 0.7**: Moderate risk-adjusted performance. Not competitive against diversified passive alternatives on a risk-adjusted basis alone.
- **CAGR = 17.2%**: Attractive in isolation but the risk metrics erode its value substantially.
- **Fees = $7,366 on $40k initial**: ~18% of starting capital consumed by fees over the backtest. Turnover of 6%/day compounds cost over long horizons.
- **Second backtest entry (2026-05-09T20:05:54Z)**: All metrics are blank — validation against confirmed strategy code is still pending.
- **Concentration**: MAX_HOLDINGS=10, MAX_NAMES_PER_SECTOR=2. At full deployment the top 2 sectors can each hold 20% of the equity book (2 × 12% cap). This is a meaningful concentration risk.
- **BIL fallback behavior**: Residual and full risk-off allocate to BIL. Unknown how often BIL is triggered in backtests — frequency data not captured in log.
- **Startup behavior**: SPY is listed as a temporary startup fallback. Duration and frequency of SPY-hold startup periods not documented; could introduce unintended SPY beta at portfolio start.

### Hypotheses

1. **Raise BREADTH_THRESHOLD (0.55 → 0.62)**: A stricter breadth requirement would exit risk-on earlier during market deterioration, potentially reducing max drawdown by 5–8 percentage points with modest CAGR cost.
2. **Reduce MAX_POSITION_WEIGHT (0.12 → 0.08)**: Lowering the single-stock cap reduces the impact of any one name on drawdown and may improve PSR by smoothing return variance.
3. **Increase MAX_HOLDINGS (10 → 20)**: Wider diversification reduces idiosyncratic drawdown, increases PSR by lowering monthly return variance, and may shorten recovery periods.
4. **Add a secondary faster regime filter**: A 50-day SMA crossover on SPY as a secondary confirmation could accelerate risk-off transitions and reduce drawdown depth without permanently raising the breadth bar.
5. **Position-level trailing stop (15% from 52-week high)**: Would close individual losing positions faster than the current SMA/momentum exit, capping per-stock contribution to portfolio drawdown.
6. **Reduce RISK_ON_EQUITY_ALLOC (0.90 → 0.80)**: Holding 20% in BIL at all times during risk-on would act as a structural shock absorber, trading ~1–2 pp of CAGR for meaningful drawdown reduction.
7. **Log BIL trigger frequency**: Instrument the strategy to count and record how often the breadth/regime filter forces BIL allocation. Without this data, evaluating risk-off behavior is guesswork.

### Rejected ideas

- **Options hedging**: Excluded — CLAUDE.md prohibits options trading.
- **Crypto diversification**: Excluded — CLAUDE.md prohibits crypto.
- **Short selling**: Excluded unless explicitly reviewed and approved by human.
- **Discretionary news/catalyst overrides**: Excluded — CLAUDE.md prohibits discretionary trading.
- **Leverage**: Not proposed — no evidence leverage improves risk-adjusted returns here.

### Validation needed

1. Confirm second backtest entry (2026-05-09T20:05:54Z) metrics match the code in `quantconnect/main.py` exactly.
2. Compare backtest results to SPY buy-and-hold, BIL, and a 60/40 benchmark over the same period.
3. Accumulate at least 14 days of paper trading data before paper vs. backtest comparison.
4. Record BIL trigger frequency and duration in future backtest notes.
5. Document SPY startup fallback duration and any drift it introduces.

---

## Review 2026-05-09 (Second pass — 21:44 UTC)

### Account snapshot

- Equity: $99,619.78 | Cash: $99,619.78 (100% cash — no positions)
- Day P&L: +$72.21 | Drawdown from HWM: 0.00%
- HWM: $99,619.78 (set 2026-05-09)

### Evidence counted

- Paper trading days: **1** (2026-05-09 only — minimum 14 required)
- Signal checks reviewed: **3** (all 2026-05-09)
- Trade execution events reviewed: **2** (both DRY_RUN, both post-market)
- Complete entry/exit cycles: **0**
- Real orders placed: **0**

### Evidence sufficiency

**INSUFFICIENT** — still below the 14-day minimum. However, a clear operational pattern has been identified and is documented below under operational health.

### Operational health

**Finding — Post-market execution timing (moderate concern):**
Both trade execution runs occurred at 21:24 UTC and 21:27 UTC (5:24–5:27 PM ET). US markets close at 20:00 UTC (4:00 PM ET). This means execution was triggered ~85 minutes after market close.

Impact observed: 8 of 11 target positions (KO, WMT, GOOGL, MRK, XOM, NVDA, LLY, AVGO) were tagged `skipped_wide_spread`. These are highly liquid S&P 500 constituents with typical intra-day spreads of 1–5 bps, well below the 100 bps maximum. Post-close, bid-ask data from Alpaca is stale or absent, producing artificially wide computed spreads. The spread guard is **working correctly** — it is correctly rejecting stale quotes — but the root cause is that execution is being run outside market hours.

Three positions (PEP, AMZN, AMD) reached `dry_run` status, suggesting their post-close quote data happened to satisfy the spread check. This inconsistency further confirms the issue is data quality at execution time, not the stocks themselves.

**What the market clock guard did:** The guard prevented zero actual orders (DRY_RUN=true handles that separately). It did not prevent the execution routine from running and performing the spread check against stale data.

**No other operational errors:** No duplicate orders, no unexplained positions, no API errors, no strategy hash mismatch.

### Top concerns

1. **Post-market execution timing**: Scheduler triggering trade execution after close causes most orders to hit the spread guard. Before DRY_RUN is removed, execution timing must be verified or the clock guard must cleanly short-circuit the run before spread checks occur.
2. **PSR = 14% from backtest**: Carries forward — no new paper data to confirm or refute.
3. **Max drawdown = 34.9% from backtest**: Carries forward.
4. **No real positions yet**: Portfolio has been 100% cash since inception. No paper trading evidence of live execution behavior.

### Ideas proposed

All four candidate experiments (A–D) from the prior 2026-05-09 review carry forward unchanged. No new parameter-change hypotheses added this pass due to insufficient data.

**New operational idea (not a parameter change):**
- **Execution timing diagnostic**: Verify that the trade execution scheduler fires only within market hours, or that the market clock guard is wired to exit cleanly before the spread-check loop when the market is closed. This is a diagnostic action, not a strategy parameter change. Files potentially involved: `scripts/run_trade_execution.py`. No config/strategy.json edit required.

### Ideas rejected this pass

- No new ideas rejected.
- Options, crypto, shorting, leverage, discretionary overrides: standing rejections per CLAUDE.md.

### Ideas deferred

- Secondary 50-day SMA regime filter (Hypothesis 4 from prior review): deferred pending paper data.
- Position-level trailing stop (Hypothesis 5 from prior review): deferred pending paper data.

### Candidate PR justified?

**No.** Insufficient paper trading evidence (1 day, 0 real trades). The execution timing issue is a diagnostic concern, not yet confirmed as a bug requiring a code change — it may be intentional design for the DRY_RUN validation workflow.

Decision: insufficient evidence — continue collecting data.
