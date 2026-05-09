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
