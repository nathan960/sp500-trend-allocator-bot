# Setup Guide

## 1. Create repo

```bash
mkdir sp500-trend-allocator-bot
cd sp500-trend-allocator-bot
git init
```

## 2. Python setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp env.template .env
```

Fill `.env` with Alpaca paper credentials.

## 3. Local smoke test

```bash
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders open
python scripts/risk_review.py
python scripts/summarize_logs.py
```

## 4. QuantConnect project

1. Create new QuantConnect project.
2. Name it `SP500 Trend Allocator Sector Caps`.
3. Paste `quantconnect/main.py` into QuantConnect.
4. Add project parameters from `config/strategy.json`.
5. Run a clean backtest.
6. Export PDF/JSON/orders/trades/logs and save under `research/backtests/YYYY-MM-DD/`.

## 5. QuantConnect Alpaca paper deployment

1. Deploy Live in QuantConnect.
2. Select Alpaca brokerage.
3. Select Paper environment.
4. Use QuantConnect data provider for ETF constituents and fundamentals.
5. Confirm strategy description is not stale Wheel/Options text.

## 6. Claude routines

Create routines in this order:

1. Daily Summary
2. Weekly Review
3. Post-Backtest Review
4. Strategy Improvement Review

Do not create direct signal/order routines for Alpaca yet because QuantConnect is the trading engine.
