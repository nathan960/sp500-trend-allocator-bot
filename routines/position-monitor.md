You are running the S&P 500 allocator position monitor.

Rules:
- Do not place orders.
- Do not edit any strategy files.
- Read Alpaca state and memory only.
- Write memory files and push to main.

Steps:
1. Verify env vars are set without printing values.
2. Run:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_position_monitor.py
3. Check stop-loss and trailing-stop alerts in output.
4. If any STOP-LOSS or TRAILING-STOP flag appears:
   - Do NOT automatically place exit orders.
   - Append a note to memory/RISK-STATE.json paused=true with pause_reason.
   - Notify the human for manual review.
5. Commit and push memory:
   git add memory
   git commit -m "position-monitor $(date -u +%Y-%m-%dT%H:%M:%SZ)" || true
   git fetch origin main
   git rebase origin/main || (git rebase --abort; exit 1)
   git push origin HEAD:main
6. Send notification with summary.
