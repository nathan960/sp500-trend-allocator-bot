# Experiment Log

Experiments do not become production automatically.

---

## 2026-05-09 — Candidate Experiments (Not Yet Run)

Paper data status: INSUFFICIENT (< 14 days). All experiments below are candidates only. No experiment has been run. Human approval required before any backtest experiment is executed and before any result is promoted.

---

### Candidate Experiment A — Raise Breadth Threshold

**Status**: Candidate — not yet run  
**Motivation**: Max drawdown of 34.9% and 986-day recovery suggest the regime filter exits risk-on too slowly. Raising the breadth bar should produce earlier BIL transitions.  
**Parameter change**: `BREADTH_THRESHOLD` 0.55 → 0.62  
**Files affected**: `config/strategy.json` (candidate copy only, not production)  
**Hypothesis**: Max drawdown decreases by 5–8 pp; CAGR impact < 1.5 pp; drawdown recovery shortens by > 100 days.  
**Success criteria**:
- Max drawdown < 28%
- CAGR > 15.7%
- Drawdown recovery < 850 days
- Sharpe ≥ 0.7 (no degradation)

**Test plan**: Run QuantConnect backtest over the same date range as the 2026-05-09 baseline. Record all metrics. Do not promote without human review.

---

### Candidate Experiment B — Wider Holdings (Diversification)

**Status**: Candidate — not yet run  
**Motivation**: PSR = 14% is critically weak. Holding only 10 names produces high monthly return variance, which suppresses the PSR. More names should smooth returns.  
**Parameter change**: `MAX_HOLDINGS` 10 → 20  
**Files affected**: `config/strategy.json` (candidate copy only, not production)  
**Hypothesis**: PSR improves to > 30%; Sharpe variance across sub-periods narrows; max drawdown unchanged or slightly lower due to reduced single-stock impact.  
**Success criteria**:
- PSR > 30%
- Sharpe ≥ 0.7
- Max drawdown ≤ 35% (no regression)
- Fees increase < 20% (turnover acceptable)

**Test plan**: Run QuantConnect backtest over the same date range as the 2026-05-09 baseline. Record all metrics. Do not promote without human review.

---

### Candidate Experiment C — Lower Max Position Weight

**Status**: Candidate — not yet run  
**Motivation**: 12% max position weight with 10 holdings means top positions can dominate. Reducing to 8% forces broader weight distribution.  
**Parameter change**: `MAX_POSITION_WEIGHT` 0.12 → 0.08  
**Files affected**: `config/strategy.json` (candidate copy only, not production)  
**Hypothesis**: Smoother return distribution improves PSR; individual stock drawdown contribution reduced; minimal CAGR impact.  
**Success criteria**:
- PSR > 25%
- Max drawdown ≤ 33%
- CAGR > 16%

**Test plan**: Run QuantConnect backtest over the same date range as the 2026-05-09 baseline. Record all metrics. Do not promote without human review.

---

### Candidate Experiment D — Reduce Equity Allocation in Risk-On

**Status**: Candidate — not yet run  
**Motivation**: Holding 10% in BIL during risk-on is a small buffer. Raising that buffer to 20% (RISK_ON_EQUITY_ALLOC 0.90 → 0.80) may structurally dampen drawdowns.  
**Parameter change**: `RISK_ON_EQUITY_ALLOC` 0.90 → 0.80  
**Files affected**: `config/strategy.json` (candidate copy only, not production)  
**Hypothesis**: Max drawdown reduced by 2–4 pp; CAGR reduced by ~1.5–2 pp; PSR improves modestly from smoother returns.  
**Success criteria**:
- Max drawdown < 31%
- CAGR > 15%
- PSR > 20%

**Test plan**: Run QuantConnect backtest over the same date range as the 2026-05-09 baseline. Record all metrics. Do not promote without human review.

---

## 2026-05-11 — Review Update

**Experiment decision**: No new experiment started or run.

**Reason**: Paper data is insufficient (2 calendar days vs. 14-day minimum). No real trades have been submitted. No entry/exit cycle has occurred. A critical operational blocker — trade execution running outside market hours, causing systematic spread guard rejection — must be resolved before any experiment result would be meaningful.

**All four candidate experiments (A, B, C, D) remain in candidate status — not yet run.**

**New operational finding (not an experiment):**
Trade execution log entries are all timestamped outside regular market hours (earliest: 12:18 UTC = 8:18 AM ET). Signal checks during market hours (14:20-14:48 UTC = 10:20-10:48 AM ET) do not have corresponding trade execution entries. This is the most likely cause of the persistent `skipped_wide_spread` pattern affecting 8/11 target names in every run.

**Action required by human:** Verify the scheduler / cron job for the Stage 2 execution script and confirm it is configured to fire during regular trading hours (9:30–16:00 ET). This is not a strategy parameter change and does not require a PR — it is a scheduling investigation.

**Next review trigger:** When ≥ 14 calendar days of paper data exist with at least one confirmed market-hours execution run.
