You are running the S&P 500 allocator Stage 2: Trade Execution.

Rules:
- DRY_RUN=false is required to submit real paper orders.
- TRADING_MODE must be "paper" (never "live" in this routine).
- Run Stage 1 (market-data-update) immediately before this routine.
- Do not place orders if any risk gate fails — let the script exit.
- Do not modify trade_plan.json manually.
- Do not edit config/strategy.json or .env.
- Commit and push memory after run.

Pre-flight:
1. Verify env vars are set without printing values.
2. Verify TRADING_MODE=paper (not live).
3. Confirm trade_plan.json exists and was generated within the last 90 minutes.

Steps:
1. Run Stage 1 first if not already done:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_market_data_update.py
2. Run Stage 2 (dry-run to preview):
   DRY_RUN=true TRADING_MODE=paper python scripts/run_trade_execution.py
3. If the dry-run output looks correct, run with live paper orders:
   DRY_RUN=false TRADING_MODE=paper python scripts/run_trade_execution.py
4. Confirm memory/TRADE-LOG.md was appended.
5. Commit and push memory:
   git add memory
   git commit -m "trade-execution $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
   git fetch origin main
   git rebase origin/main || (git rebase --abort; exit 1)
   git push origin HEAD:main
6. Send notification:
   bash scripts/notify.sh "Stage 2 complete: orders submitted to Alpaca paper"

Or run both stages in one command:
   DRY_RUN=false TRADING_MODE=paper bash scripts/alpaca.sh run
