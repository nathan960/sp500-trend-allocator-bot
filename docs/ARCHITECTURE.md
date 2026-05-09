# Architecture

## Primary decision

Keep QuantConnect as the trading engine for this strategy.

## Why

The strategy depends on QuantConnect-native data and behavior:

- SPY ETF constituents universe
- historical constituent membership
- Morningstar sector/fundamental classifications
- QuantConnect indicator warm-up
- QuantConnect portfolio targeting

Direct Alpaca Python execution is not recommended for the first version because it would require a separate constituent and sector data pipeline.

## Components

```text
QuantConnect = strategy engine and order generation
Alpaca Paper = brokerage target through QuantConnect
Claude + GitHub + VSCode = monitoring, documentation, reporting, review, improvement proposals
Discord = concise notifications
```

## What Claude does not do

Claude does not place trades directly. Claude does not edit `quantconnect/main.py` without approval. Claude does not deploy QuantConnect.
