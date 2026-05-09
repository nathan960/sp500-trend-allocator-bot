You are running strategy improvement review.

Rules:
- Claude may propose improvements.
- Claude may not auto-edit quantconnect/main.py.
- Claude may not deploy.
- Claude may not change risk limits.
- Human approval required.

Tasks:
1. Read BACKTEST-LOG, WEEKLY-REVIEW, TRADING-STRATEGY, and config/improvement_policy.json.
2. Identify failure modes: long drawdown recovery, high drawdown, over-trading, poor PSR, weak regimes.
3. Propose hypotheses only.
4. Append to memory/IMPROVEMENT-IDEAS.md and memory/EXPERIMENT-LOG.md.
5. Commit and push memory.
