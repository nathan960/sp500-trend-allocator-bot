#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

review = f"""## {now()} Risk Review

Checklist:
- Strategy engine: QuantConnect
- Brokerage: Alpaca Paper through QuantConnect
- Direct Alpaca order placement from repo: disabled
- Options: forbidden
- Crypto: forbidden for this strategy
- Shorts: forbidden unless explicitly approved
- Max position weight controlled by QuantConnect project parameter
- Sector caps controlled by QuantConnect project parameter
- BIL fallback in risk-off

Current concerns to monitor:
- QuantConnect project metadata must match actual strategy.
- Validate exact code/report match.
- Monitor drawdown and long recovery period.
- Confirm Alpaca positions match expected equity instruments.
"""

p = Path("memory/WEEKLY-REVIEW.md")
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text((p.read_text() if p.exists() else "").rstrip() + "\n\n" + review)
print(review)
