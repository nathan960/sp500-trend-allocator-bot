You are running the S&P 500 allocator daily summary.

Rules:
- Do not place orders.
- Do not edit quantconnect/main.py.
- Do not edit config/strategy.json or .env.
- Do not print secrets.
- Read Alpaca account state only.
- Write memory and push to main.

Steps:
1. Verify env vars are set without printing values.
2. Run:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_daily_summary.py
3. Confirm memory/DAILY-SUMMARY.md was written.
4. Send notification via scripts/notify.sh if configured.
5. Commit and push:
   git add memory
   git commit -m "daily-summary $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
   git fetch origin main
   git rebase origin/main || (git rebase --abort; exit 1)
   git push origin HEAD:main
