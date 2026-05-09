# QuantConnect Deployment Checklist

## Before backtest

- Project name: `SP500 Trend Allocator Sector Caps`
- Description: `SPY constituents trend/momentum allocator with sector caps and BIL risk-off fallback.`
- No Wheel Strategy metadata.
- No Equity Options metadata unless actually used.

## Project parameters

```text
MAX_HOLDINGS = 10
MAX_POSITION_WEIGHT = 0.12
BREADTH_THRESHOLD = 0.55
RISK_ON_EQUITY_ALLOC = 0.90
MIN_MOMENTUM_6M = 0.0
MIN_MOMENTUM_12M = 0.0
MAX_NAMES_PER_SECTOR = 2
```

## Paper deployment

- Brokerage: Alpaca
- Environment: Paper
- Strategy engine: QuantConnect
- Data provider: QuantConnect
- Instruments: SPY constituents, BIL, SPY fallback
- No direct Alpaca Python order execution from this repo

## Paper validation

Minimum 14 days, preferred 30 days.

Track positions, sector exposure, BIL allocation, turnover, fees, drawdowns, rebalances, unexpected holdings, and daily/weekly summaries.
