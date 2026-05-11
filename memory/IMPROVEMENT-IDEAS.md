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

## Review 2026-05-11

### Account snapshot

- Equity: $99,297.88
- Cash: ~$99,620 (all cash — no positions held)
- High-water mark: $99,619.78 (2026-05-09)
- Drawdown from HWM: 0.32%
- Regime: RISK_ON
- Breadth: 55.2% (just above 50% threshold)
- Eligible names: 13/28 scored (NVDA dropped out vs. May 9; QCOM entered)

### Paper data status

INSUFFICIENT PAPER DATA — 2 calendar days since first signal check (2026-05-09). Minimum required is 14 calendar days. Strategy is still all cash. No real orders have been submitted. Insufficient evidence for any production parameter change.

Decision: insufficient evidence — continue collecting data.

### Signal checks reviewed: 8 total (5 on 2026-05-09, 3 on 2026-05-11)

### Trade events reviewed: 4 DRY_RUN executions — 0 real orders submitted, 0 entry/exit cycles completed

### Operational health

**CRITICAL CONCERN — Persistent `skipped_wide_spread` blocker:**
All 4 logged trade execution runs show 8 of 11 planned buys rejected as `skipped_wide_spread`. Only PEP, AMZN, and AMD pass the spread check (and are tagged `[dry_run]`, not actually submitted). Affected names: KO, WMT, GOOGL, MRK, XOM, NVDA, LLY, AVGO.

Root cause hypothesis: Trade execution runs appear to occur outside regular market hours (2026-05-11T12:18 UTC = 8:18 AM ET, pre-market). After-hours bid/ask spreads are inherently wide. The spread guard (`max_spread_bps: 100`) is correctly rejecting these. However, signal checks at 14:20 and 14:48 UTC (10:20 and 10:48 AM ET, during market hours) do not have corresponding trade execution log entries — suggesting the trade execution stage is not being triggered during market hours.

**If this diagnosis is correct**: the strategy has never attempted a trade during market hours. No portfolio can be built until execution timing is corrected.

**Other operational notes:**
- Approved strategy hash is empty in RISK-STATE.json — no strategy version formally hash-approved.
- Daily summary last run 2026-05-09; trade execution last run 2026-05-11 — mild staleness in daily P&L tracking.
- Universe shift noted: NVDA left eligible set between May 9 and May 11; QCOM entered at ~4.1% target weight. This is expected behavior as momentum scores fluctuate.

### Top concerns

1. **Execution timing / wide spread blocker** (Operational): Trade execution may be running entirely outside market hours, causing the spread guard to block all or most orders. Strategy will remain in all-cash until this is diagnosed and fixed.
2. **Approved strategy hash missing**: No formal hash approval in RISK-STATE.json. This is a governance gap.
3. **Zero entry/exit cycles**: No data exists on how the strategy behaves after building a position. All prior hypotheses (from 2026-05-09) remain unvalidated.

### New ideas proposed

**Idea 8 — Investigate and fix execution timing (Operational — not a parameter change)**
- Hypothesis: Trade execution is running pre-market, causing systematic spread-guard rejection. Correcting execution timing to run within the 9:45–15:45 ET window would allow the portfolio to build for the first time.
- Evidence: All 4 trade execution log entries are timestamped pre-market or after-hours (12:18 UTC = 8:18 AM ET). Signal checks at 14:20-14:48 UTC (during market hours) lack corresponding trade execution entries.
- Proposed change: Verify the cron/scheduler for the Stage 2 (trade execution) script and confirm it is set to fire during regular market hours (9:30–16:00 ET), not pre-market.
- Files affected: Scheduler config or cron definition (not `quantconnect/main.py`, not `config/strategy.json`).
- Expected benefit: Allows the portfolio to build. Without this, all other improvement ideas are moot.
- Failure mode: If execution timing is already correct and something else causes the wide spreads, this diagnosis is wrong — check the spread data source.
- Overfit risk: None — this is operational, not a parameter change.
- Validation required: Confirm a trade execution log entry timestamped between 9:45 and 15:45 ET, with fewer spread rejections for liquid large-caps.
- Pass/fail: Pass if ≥ 5 of 11 target names execute without spread rejection during market hours.
- Rollback: N/A — no production strategy change.
- Candidate PR justified: Not a PR — operational scheduling issue for human to investigate.

**Idea 9 — Log spread values at execution time (Diagnostics)**
- Hypothesis: Adding the observed bid/ask spread (in bps) to each trade log entry would allow direct confirmation of whether the issue is time-of-day or a data source problem.
- Evidence: Current trade log shows `[skipped_wide_spread]` with no numerical spread value recorded. Impossible to distinguish 101 bps vs. 500 bps without this data.
- Proposed change: Add spread bps to trade log output for each skipped and executed order.
- Files affected: The Stage 2 execution script (not `quantconnect/main.py`).
- Expected benefit: Immediately diagnoses whether the spread issue is timing-related or data-related.
- Overfit risk: None — diagnostic only.
- Candidate PR justified: Deferred — human should first check the scheduler.

### Ideas deferred from 2026-05-09

All seven hypotheses from the 2026-05-09 review (breadth threshold, position weight, holdings count, secondary regime filter, trailing stop, equity allocation, BIL logging) remain deferred pending 14+ days of paper data and at least one completed entry/exit cycle.

### Candidate PR status

Not justified. Operational execution timing issue must be diagnosed first. Zero paper trading data means no parameter change is evidence-backed.

---

## Research Context Hypotheses — 2026-05-11

*Derived from macro/market research. No paper data yet. All deferred pending execution fix and 14-day minimum paper data.*

**Idea 10 — Resolve breadth_threshold config discrepancy (Governance)**
- Observation: `config/strategy.json` sets `breadth_threshold: 0.50`; `memory/TRADING-STRATEGY.md` documents `BREADTH_THRESHOLD: 0.55`. These differ by 5 pp, which is material when live breadth reads 51.7%.
- Hypothesis: The live system may be operating with a lower breadth bar than intended, which could result in building equity positions during marginally-supported market conditions.
- Proposed action: Human to confirm which value governs the live/paper system and reconcile the two files.
- Files affected: `config/strategy.json` (if change needed) and `memory/TRADING-STRATEGY.md`.
- Evidence needed: Confirm which config field the production code reads. No backtest evidence yet.
- Candidate PR: Not yet — governance clarification needed first.

**Idea 11 — Evaluate energy exposure given Iran/oil shock (Research only)**
- Observation: XOM is currently a top-7 target weight (~7.5%). Oil prices are volatile in the $90–120 range due to the Iran/Hormuz disruption. XOM momentum and trend are strong, so it passes the filter naturally.
- Hypothesis: In a sustained oil-shock environment (crude sustained above $100), the strategy may naturally over-allocate to energy via momentum, increasing sector concentration risk beyond the 2-names cap.
- Note: Current `max_names_per_sector: 3` allows up to 3 energy names at up to 15% each = 45% theoretical energy cap. This is significantly wider than the 2-name cap documented in `TRADING-STRATEGY.md` (which says `MAX_NAMES_PER_SECTOR: 2`).
- Proposed action: Audit whether the live config values (`max_names_per_sector: 3`, `max_position_weight: 0.15`) vs. documented values (`MAX_NAMES_PER_SECTOR: 2`, `MAX_POSITION_WEIGHT: 0.12`) represent an intentional loosening or another config discrepancy.
- Evidence needed: Review change history on `config/strategy.json`. No parameter change proposed.
- Candidate PR: Not yet.

**Idea 12 — Breadth as leading indicator of regime flip (Research hypothesis)**
- Context: External data shows only ~52% of S&P 500 names above their 50-day MA while the index makes all-time highs. Strategy breadth (universe-specific, 28 names) mirrors this at 51.7% in the latest signal.
- Hypothesis: Narrow breadth at index all-time highs historically precedes either (a) breadth expansion confirming the rally, or (b) breadth contraction leading to a modest correction. The strategy's SPY 200-day filter would need a sustained drawdown (typically 10–15%+ from all-time highs) to trigger risk-off — but the breadth filter could trigger first if participation deteriorates.
- Research idea: Track strategy breadth reading across multiple consecutive signal checks to build a time series. If breadth trends downward over 2–3 weeks while the index stays near highs, that is early warning of a possible risk-off flip.
- Evidence needed: 14+ days of daily signal logs with breadth readings.
- Candidate PR: Not yet — monitoring hypothesis only.
