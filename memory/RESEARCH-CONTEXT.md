# Research Context

---

## 2026-05-11 — Research Context Entry

### Market Regime

S&P 500 closed at 7,412.84 on May 10, above 7,400 for the first time, posting a sixth consecutive weekly gain — the longest win streak since 2024. The index finished April at a fresh all-time high of ~7,209 (+strongest April since 2020). The broad trend remains clearly RISK_ON: the index is comfortably above its 200-day SMA. RSI entered overbought territory as of May 6 for the S&P 500, Nasdaq 100, Communication Services, and Information Technology. A near-term digestion phase is plausible before any resumption.

**Strategy consistency:** The strategy's RISK_ON signal is consistent with these conditions. No regime change is indicated.

### Rates / Fed / Inflation

- CPI running ~3.3%; economists at Nationwide project a summer peak near 4.5% — more than double the Fed's 2% target.
- Dual price shocks: Trump tariffs + Iran war/Strait of Hormuz disruption (~20 million bbl/day at risk during blockade).
- FOMC held rates steady at its April 29 meeting. Median longer-run rate projection: 3.1% (from March 18 SEP).
- Bank of America and J.P. Morgan now project no cuts until H2 2027; multiple Fed officials have signaled the next move could be a hike.
- Higher-for-longer rate environment benefits BIL (the risk-off fallback) in absolute yield terms. BIL yield remains attractive relative to its 2020–2022 near-zero period.

**Strategy relevance:** Elevated rates reduce the relative opportunity cost of holding BIL during risk-off. If the breadth threshold triggers a risk-off shift, BIL return will be meaningfully positive rather than near-zero. No change to strategy parameters warranted from rates alone.

### Sector Rotation / Leadership

- **Technology (XLK):** Confirmed sector leader — strongest 5-day and 20-day relative strength. AI infrastructure capex is not slowing; hyperscaler guidance stepped higher. Semiconductors (AVGO, NVDA, AMD, QCOM) are the sub-sector leader within tech.
- **Energy (XOM):** Back in favor. Supply discipline meets elevated oil prices ($90–120/bbl range). XOM free cash flow profile strong at current crude prices.
- **Consumer Staples (KO, WMT, PEP):** Defensive quality names reaching all-time highs. Leadership has rotated toward these from pure growth mega-caps.
- **Healthcare (MRK, LLY):** Solid performers; LLY GLP-1 franchise and MRK oncology pipeline remain catalysts.
- **Mega-cap Concentration Risk:** ~70% of year-over-year S&P 500 earnings estimate increases in 2026 driven by AMZN, GOOGL, and META alone. Index rally is narrow at the mega-cap level even as Consumer Staples and Energy also make all-time highs.

**Strategy relevance:** The current portfolio composite (KO, WMT, PEP, GOOGL, MRK, AMZN, XOM, AVGO, LLY, AMD, QCOM) is well-aligned with identified sector leadership. The ATR-based weighting naturally favors lower-volatility names (KO, WMT, PEP at top weights), which is coherent with a defensive-quality rotation environment. NVDA dropped from eligible set between May 9 and May 11; QCOM entered. This is consistent with normal momentum score fluctuation and requires no intervention.

### Volatility / Risk Appetite

- VIX at ~17–18 as of May 10-11, down sharply from a March peak above 31.
- VIX is still +15.5% YTD — elevated relative to 2025 baseline.
- Oil below $100/bbl on May 6 (Iran deal speculation); reversed to ~$100 again by May 10 after Iran rejected U.S. terms.
- Risk appetite is recovering but geopolitical optionality remains elevated.

**Strategy relevance:** VIX ~18 is consistent with a normal risk-on environment. The VIX spike to 31 in March (likely tied to initial Iran conflict escalation and tariff shock) did not breach the SPY 200-day SMA sufficiently to trigger a risk-off regime in this strategy. If VIX were to spike again above 25–30 alongside index weakness, breadth could fall below 50% and trigger BIL allocation.

### Breadth Analysis

- Strategy breadth: 55.2% (most recent signals); dropped to 51.7% in the 2026-05-11T21:14 check.
- External data: Only ~52% of S&P 500 stocks traded above their 50-day MA as of May 7.
- The index is making all-time highs on concentrated mega-cap and sector leadership, NOT broad participation.
- Eligible names: dropped from 14/28 (May 9) to 12/28 (May 11 final signal) — a 14% reduction in two days.

**Critical observation:** The strategy's breadth reading (51.7% in the latest signal) is just 1.7 percentage points above the 50% threshold. If breadth deteriorates further — consistent with the external observation that only ~52% of SPX names are above their 50-day MA — the strategy could flip to a partial or full BIL allocation at the next rebalance. This would be appropriate behavior, not a malfunction.

**Note:** The breadth threshold in `config/strategy.json` is currently set to 0.50, while `memory/TRADING-STRATEGY.md` documents it as 0.55. This discrepancy should be confirmed. If the live threshold is truly 0.50, the current 51.7% reading is only 1.7 pp from a trigger. If 0.55, the strategy is already below the documented threshold in the latest signal.

### Risks to Monitor

1. **Breadth deterioration:** With only 51.7% breadth and a threshold near 50%, a modest pullback in participation could flip the strategy to BIL. This is the primary near-term operational risk to the portfolio build.
2. **Iran / Strait of Hormuz:** Ongoing Hormuz disruption affects ~20 million bbl/day. Re-escalation would spike oil, compress consumer spending, and likely damage breadth further. XOM is a natural beneficiary; consumer names (KO, WMT, PEP) may be mixed.
3. **Inflation persistence:** If CPI approaches 4.5% by summer, rate-hike probability rises materially. Rising rates pressure growth equities (GOOGL, AMZN, AVGO) and could shift sector leadership further toward Energy and Staples.
4. **Overbought RSI conditions:** S&P 500 overbought as of May 6. A 3–5% pullback would be technically expected and would be absorbed by the 200-day SMA filter (currently well below spot), but would push breadth lower.
5. **Execution timing (operational):** As noted in IMPROVEMENT-IDEAS.md, all trade execution runs to date have been pre-market, causing systematic `skipped_wide_spread` rejections. The portfolio cannot be built until this is resolved. This is the single highest-priority operational item.
6. **Breadth config discrepancy:** `config/strategy.json` sets `breadth_threshold: 0.50` while `TRADING-STRATEGY.md` documents `BREADTH_THRESHOLD: 0.55`. If the live system uses 0.50, the 51.7% reading remains risk-on. If 0.55, the strategy should have triggered BIL in the latest signal. Human review needed.

### No Production Changes Recommended

No production changes to `quantconnect/main.py`, `config/strategy.json`, or risk limits are supported by current evidence. Paper trading data accumulation has not yet reached the minimum 14-day threshold. All prior hypotheses remain deferred.

---
