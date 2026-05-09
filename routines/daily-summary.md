You are running the S&P 500 allocator daily summary.

Rules:
- Do not place trades.
- Do not edit quantconnect/main.py.
- Do not create `.env`.
- Do not print secrets.
- Read Alpaca account state only.
- Write memory and push to main.

Steps:
1. Verify env vars are set without printing values.
2. Read CLAUDE.md, memory/PROJECT-CONTEXT.md, memory/TRADING-STRATEGY.md.
3. Run:
   bash scripts/alpaca.sh account
   bash scripts/alpaca.sh positions
   bash scripts/alpaca.sh orders open
4. Append concise summary to memory/DAILY-SUMMARY.md.
5. Send notification via scripts/notify.sh if configured.
6. Commit and push:
   git add memory
   git commit -m "daily-summary $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
   git fetch origin main
   git rebase origin/main || (git rebase --abort; exit 1)
   git push origin HEAD:main
