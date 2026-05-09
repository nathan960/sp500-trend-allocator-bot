You are running the S&P 500 allocator weekly review.

Rules:
- Do not place orders.
- Do not edit production strategy code or config files.
- Review only.

Steps:
1. Read memory/TRADING-STRATEGY.md (if present), memory/DAILY-SUMMARY.md, memory/TRADE-LOG.md, memory/SIGNAL-LOG.md.
2. Run:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_weekly_review.py
3. Summarize: week P&L, drawdown, open positions, any risk events.
4. Note any concerning patterns (large drawdown, sector concentration, missed signals).
5. Append to memory/WEEKLY-REVIEW.md.
6. Send concise notification with week P&L and drawdown.
7. Commit and push memory to main.
