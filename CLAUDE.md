# Claude Operating Rules

This repo manages the **S&P 500 Trend Allocator with Sector Caps**.

## Critical identity

- This is not the BTC/ETH crypto bot.
- This is not an options bot.
- This is not the YouTuber's discretionary stock-catalyst bot.
- This is a QuantConnect S&P 500 constituent trend/momentum allocator.

## Trading engine

QuantConnect is the trading engine.
Alpaca is the brokerage target through QuantConnect paper/live deployment.

## Claude may

- Monitor Alpaca account state.
- Summarize QuantConnect paper/live behavior.
- Write memory files.
- Review backtests.
- Propose research ideas.
- Create candidate PRs after explicit human request.

## Claude may not

- Place direct Alpaca orders.
- Edit `quantconnect/main.py` automatically.
- Deploy QuantConnect live automatically.
- Approve live trading.
- Use discretionary news/catalyst decisions.
- Trade options.
- Trade crypto.
- Change risk limits without approval.
- Create or commit `.env`.
- Print secrets.
- Force-push.

## Git memory

All persistent memory lives in `memory/*.md` and `memory/*.json`.
Cloud routines must commit and push to `main`.

## Production-change rule

Any change to `quantconnect/main.py`, `config/strategy.json`, or risk limits must be proposed as a candidate change and reviewed by the human before deployment.
