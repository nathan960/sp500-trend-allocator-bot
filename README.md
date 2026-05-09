# S&P 500 Trend Allocator Bot

This repo manages the **S&P 500 Trend Allocator with Sector Caps** strategy.

This is **not** the BTC/ETH crypto bot and **not** the YouTuber's stock-catalyst bot. The YouTuber guide is used only as an operating architecture template: Git memory, VSCode, Claude routines, notifications, and strict setup discipline.

## Strategy identity

- Trading engine: **QuantConnect**
- Brokerage target: **Alpaca Paper via QuantConnect**
- Universe: **SPY ETF constituents**
- Fallback instruments: **BIL** risk-off fallback and **SPY** provisional startup fallback
- Strategy type: long-only equity trend/momentum allocator
- No crypto
- No options
- No direct Alpaca order placement from this repo
- Claude may monitor, summarize, research, and propose candidate changes, but may not directly deploy or mutate production strategy rules.

## Core strategy rules

- SPY market regime filter
- SPY 200-day SMA trend check
- SPY 126-day momentum check
- S&P 500 constituent stock-level 200-day SMA trend filter
- 126-day and 252-day momentum filters
- blended 6m / 12m momentum ranking
- inverse ATR% position sizing
- sector caps
- max holdings
- max per-position weight
- BIL fallback in risk-off periods

## First setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp env.template .env
```

Fill `.env` with Alpaca **paper** credentials. Never commit `.env`.

## QuantConnect

The QuantConnect strategy lives in:

```text
quantconnect/main.py
```

Create a new QuantConnect project named:

```text
SP500 Trend Allocator Sector Caps
```

Paste `quantconnect/main.py` into QuantConnect and run a clean backtest.

## Claude routines

Start with read-only routines:

1. Daily Summary
2. Weekly Review
3. Post-Backtest Review
4. Strategy Improvement Review

Claude routines should push memory to `main` using `git push origin HEAD:main` and should not edit `quantconnect/main.py` unless you explicitly approve a candidate PR.

## Safety

Live trading is disabled by policy. Paper trading through QuantConnect + Alpaca should be validated for at least 14-30 days before any live discussion.
