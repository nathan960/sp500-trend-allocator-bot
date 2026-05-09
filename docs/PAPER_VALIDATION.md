# Paper Validation Plan

Minimum 14 days, preferred 30 days.

## Track

- equity
- cash
- open positions
- BIL weight
- SPY fallback state
- sector counts
- realized/unrealized P&L
- fees
- turnover
- drawdown
- deployment errors

## Continue paper if

- QuantConnect deployment runs without runtime errors
- Alpaca positions match expected instruments
- memory logs update daily
- weekly review completes
- no unexpected orders or holdings

## Stop and inspect if

- report/project metadata says Wheel or Options
- unexpected options or crypto positions appear
- BIL fallback not tradable
- sector caps fail
- strategy stops rebalancing
- QuantConnect runtime errors occur
