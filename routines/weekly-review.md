You are running the S&P 500 allocator weekly review.

Rules:
- Do not place trades.
- Do not edit production strategy code.
- Do not deploy QuantConnect.
- Review only.

Steps:
1. Read memory/TRADING-STRATEGY.md, memory/BACKTEST-LOG.md, memory/DAILY-SUMMARY.md, memory/DEPLOYMENT-LOG.md.
2. Run: python scripts/risk_review.py
3. Append weekly review to memory/WEEKLY-REVIEW.md.
4. Send concise notification.
5. Commit and push memory to main using `git push origin HEAD:main`.
