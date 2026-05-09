You are running the S&P 500 allocator strategy improvement review.

Rules:
- Claude may propose improvements only.
- Claude may NOT auto-edit config/strategy.json, config/universe.json, or src/*.py.
- Claude may NOT deploy or submit orders.
- Claude may NOT change risk limits without human approval.
- Human approval required for all changes.

Tasks:
1. Read memory/IMPROVEMENT-IDEAS.md, memory/WEEKLY-REVIEW.md, memory/SIGNAL-LOG.md, memory/TRADE-LOG.md.
2. Run:
   DRY_RUN=true TRADING_MODE=paper python scripts/run_strategy_improvement_review.py
3. Identify failure modes: long drawdown recovery, over-trading, sector concentration, weak regimes.
4. Propose concrete hypotheses (e.g., "extend trend_lookback from 200 to 252 to reduce false signals").
5. Append hypotheses to memory/IMPROVEMENT-IDEAS.md.
6. Append experiment notes to memory/EXPERIMENT-LOG.md.
7. Commit and push memory.

Do NOT create candidate PRs unless explicitly instructed by the human.
