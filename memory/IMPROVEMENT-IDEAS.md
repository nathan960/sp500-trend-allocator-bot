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
