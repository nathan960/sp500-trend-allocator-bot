#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone
import json

def read(path):
    p = Path(path)
    return p.read_text() if p.exists() else ""

summary = {
    "timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "daily_summary_chars": len(read("memory/DAILY-SUMMARY.md")),
    "weekly_review_chars": len(read("memory/WEEKLY-REVIEW.md")),
    "deployment_log_chars": len(read("memory/DEPLOYMENT-LOG.md")),
    "backtest_log_chars": len(read("memory/BACKTEST-LOG.md")),
    "notes": "Repo log summary for S&P 500 trend allocator."
}
Path("memory/LOG-SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
