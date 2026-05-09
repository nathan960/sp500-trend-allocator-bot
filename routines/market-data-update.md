You are running the S&P 500 allocator Stage 1: Market Data + Signal Plan.

Rules:
- Do not place orders. This routine is structurally incapable of trading.
- Do not edit config/strategy.json or config/universe.json.
- Do not edit .env.
- Do not print secrets.
- Write data/latest/ and memory/ only.
- Commit and push memory to main after run.

Steps:
1. Verify env vars are set (ALPACA_API_KEY, ALPACA_SECRET_KEY) without printing values.
2. Run:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_market_data_update.py
3. Confirm data/latest/trade_plan.json was written.
4. Confirm memory/SIGNAL-LOG.md was appended.
5. Confirm memory/DATA-LOG.md was appended.
6. Commit and push memory:
   git add memory data/latest/.gitkeep
   git commit -m "signal-update $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
   git fetch origin main
   git rebase origin/main || (git rebase --abort; exit 1)
   git push origin HEAD:main
7. Send notification:
   bash scripts/notify.sh "Stage 1 complete: signal plan written"

This routine is safe to run at any time. It never submits orders.
