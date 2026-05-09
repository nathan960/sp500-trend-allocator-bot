---
description: Read-only preflight for S&P 500 allocator repo.
---

Run:
```bash
git status --short
git ls-files .env
python -m compileall scripts
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders open
```

Do not edit files. Do not place orders.
