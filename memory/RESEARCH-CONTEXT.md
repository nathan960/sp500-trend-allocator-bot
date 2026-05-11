# Research Context

---

## 2026-05-11 — Market Context Summary

### Sources consulted
- Crestwood Advisors May 2026 Economic and Market Update
- CNBC Stock Market Live May 11, 2026
- 24/7 Wall St. May 5–6, 2026
- Federal Reserve FOMC April 29, 2026 press release
- iShares Fed Outlook 2026; J.P. Morgan Global Research; Bank of America / CBS News
- Investing.com sector rotation analysis; QuantLake sector regime post May 8, 2026
- HeyGoTrade S&P 500 Mid-Year Outlook 2026; StoneX May 2026 seasonality commentary

### S&P 500 regime

- SPY closed April at an all-time high of 7,209 — second-best April performance since 1945 — and extended to ~7,413 by May 11–12. Both SPY and Nasdaq set fresh all-time intraday highs.
- Q1 EPS growth: 15.1% YoY. Sixth consecutive quarter of double-digit earnings growth.
- Forward 12-month P/E: 20.9 — above the 5-year avg (19.9) and 10-year avg (18.9). Elevated but not extreme.
- RSI moved into overbought territory as of May 6, alongside overbought readings for Communication Services and Information Technology sectors.
- "Sell in May" seasonality commentary suggests the pattern may not apply given current earnings momentum, but short-term overbought condition is a near-term risk.
- **Assessment**: Clearly RISK_ON by price and earnings trends. Strategy signal is consistent with market reality.

### Rates / Fed / inflation

- Inflation: 3.3% CPI, well above the Fed's 2% target. Risk of peak near 4.5% this summer driven by higher energy prices tied to the Iran conflict.
- Fed held rates at its April 29 FOMC. No cuts expected through 2026. Bank of America sees cuts delayed to 2H 2027. J.P. Morgan sees possible 25bps hike in Q3 2027.
- Implication: BIL (risk-off fallback) continues to earn meaningful yield. Elevated rates compress equity multiples on the margin but have not broken the uptrend.

### Geopolitical context

- Iran war is the key macro risk. It has driven energy prices higher and kept inflation elevated.
- U.S.-Iran nuclear deal talks are progressing; oil is retreating on deal optimism as of May 5–6, easing energy-price inflation fears near term.
- Deal uncertainty persists — escalation remains a tail risk.

### Sector rotation

- **Leading**: Consumer Staples (XLP), Energy (XLE), Industrials (XLI), Materials (XLB) — defensive and cyclical names at or near all-time highs.
- **Lagging** (20-day relative strength): Technology (XLK), Communication Services (XLC), Consumer Discretionary (XLY), Financials (XLF).
- **Short-term tech leadership** (5-day): XLK is the top relative-strength sector on a 5-day basis — short-term divergence from 20-day trend.
- Semiconductors remain strong driven by AI infrastructure spend and hyperscaler capex.
- A "Great Rotation" is noted in several sources: equal-weight names and defensive/cyclical sectors outperforming cap-weighted mega-cap tech on an intermediate basis.

### Volatility / risk appetite

- VIX near 17–18 as of May 6–11, well off the late-March peak above 31.
- A VIX of 17 sits at the low end of the normal 15–20 band — options market pricing ~1% daily SPY move. Hedging demand has cooled.
- Upcoming event risks: FOMC meeting, non-farm payrolls, April CPI — any could push VIX back through 20.

---

### Relevance to current strategy

**Current signal state (2026-05-11T21:14 UTC):**
- Regime: RISK_ON
- Breadth: 51.7% (declining from 55.2% over the prior 36 hours; approaching the 50% threshold in config/strategy.json)
- Active holdings (target): KO 15.0%, WMT 12.8%, GOOGL 9.8%, MRK 9.5%, AMZN 9.3%, XOM 8.6%, AVGO 7.7%, LLY 7.6%, AMD 4.9%, QCOM 4.7%
- Cash buffer: 10.2%
- No positions held in Alpaca — all DRY_RUN or skipped_wide_spread (see IMPROVEMENT-IDEAS Idea 8)

**Portfolio / context alignment:**
- Consumer Staples (KO, WMT) at ~27.8% of target book: consistent with current sector leadership; defensives and Consumer Staples are the 20-day leaders.
- Energy (XOM) at 8.6%: consistent with sector rotation toward energy leadership.
- Healthcare (MRK, LLY) at ~17.1%: defensive tilt suits the "elevated but overbought" market environment.
- Tech (GOOGL, AVGO, AMD, QCOM) at ~27.1%: partial exposure to the sector currently lagging on a 20-day basis but with strong AI/semiconductor tailwinds on a 5-day basis.
- The signal is tilting heavily defensive, which is appropriate given the sector rotation context.

**Discrepancy alert — TRADING-STRATEGY.md vs config/strategy.json:**

| Parameter            | TRADING-STRATEGY.md | config/strategy.json |
|----------------------|---------------------|----------------------|
| MAX_HOLDINGS         | 10                  | 12                   |
| MAX_POSITION_WEIGHT  | 0.12                | 0.15                 |
| BREADTH_THRESHOLD    | 0.55                | 0.50                 |
| MAX_NAMES_PER_SECTOR | 2                   | 3                    |
| RISK_ON_EQUITY_ALLOC | 0.90                | 0.95                 |

The operative file is config/strategy.json (referenced by strategy_version 2.0). TRADING-STRATEGY.md appears to describe an earlier parameter set. This creates governance ambiguity. Human review recommended to reconcile or annotate which is authoritative.

---

### Risks to monitor

1. **Breadth deterioration approaching threshold**: Latest reading is 51.7%, only 1.7pp above the 50% risk-off trigger. An uptick in market volatility (FOMC, CPI, Iran escalation) could push breadth below 50% and force a full BIL allocation. Monitor weekly.
2. **Inflation re-acceleration**: 3.3% current; 4.5% peak possible by summer. If energy prices re-spike on Iran escalation, inflation prints could surprise to the upside, pressuring equity multiples and breadth.
3. **Execution timing blocker**: Strategy holds zero positions despite a RISK_ON signal. Until Idea 8 (execution timing) is resolved, all market context is moot for actual portfolio construction.
4. **Consumer Staples concentration**: KO + WMT in the current signal = ~27.8% of target book in a single sector (2 of 3 allowed names). If consumer staples rotates out, that is a large rebalancing event.
5. **SPY RSI overbought**: Short-term pullback risk in the index could temporarily test the 200-day SMA filter. The 200-day SMA is the primary regime gate — SPY must stay above it for RISK_ON to hold.
6. **Near-term event calendar**: FOMC, NFP, April CPI clustered close together — could cause a temporary spike in VIX toward 20+, which would not itself trigger risk-off but would affect breadth and spreads.
7. **BIL yield duration risk**: If the Fed eventually cuts (2H 2027 at earliest), BIL yield will compress. The risk-off leg of the strategy is currently generating ~5% yield on cash held; this advantage diminishes when rates fall.

---

### No production changes recommended

No changes to quantconnect/main.py, config/strategy.json, or risk parameters are proposed. All observations are for research context only. Paper data accumulation continues to be insufficient for any evidence-backed parameter change.
