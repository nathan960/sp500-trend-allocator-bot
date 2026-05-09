# Project Context

This repo manages the S&P 500 Trend Allocator with Sector Caps.

The strategy is no longer the BTC/ETH crypto bot.

## Current architecture

- QuantConnect is the trading engine.
- Alpaca paper is the brokerage target through QuantConnect.
- Claude/GitHub/VSCode are used for monitoring, reporting, docs, research, and candidate improvements.
- Claude must not place discretionary trades.
- Claude must not edit QuantConnect `main.py` without human approval.
- Claude must not deploy live/paper changes automatically.
