# Trading Strategy

## Name

S&P 500 Trend Allocator with Sector Caps

## Universe

SPY ETF constituents.

## Instruments

- SPY constituents
- SPY temporary startup fallback
- BIL risk-off fallback

## Rules

1. Use SPY market regime filter.
2. SPY must be above 200-day SMA.
3. SPY 126-day ROC must be positive.
4. Breadth threshold must pass.
5. Candidate stocks must be above their own 200-day SMA.
6. Candidate stocks must pass 126-day and 252-day momentum filters.
7. Rank candidates by blended 6-month / 12-month momentum.
8. Weight selected stocks by inverse ATR%.
9. Enforce max holdings.
10. Enforce max position weight.
11. Enforce max names per sector.
12. Allocate residual to BIL.
13. In risk-off, allocate to BIL.
14. No options.
15. No crypto.
16. No shorting unless explicitly reviewed and approved.
17. No Claude discretionary trading.

## Current default parameters

- MAX_HOLDINGS: 10
- MAX_POSITION_WEIGHT: 0.12
- BREADTH_THRESHOLD: 0.55
- RISK_ON_EQUITY_ALLOC: 0.90
- MAX_NAMES_PER_SECTOR: 2
