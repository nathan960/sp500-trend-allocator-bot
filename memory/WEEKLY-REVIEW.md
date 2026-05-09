# Weekly Review

## Weekly Review — 2026-05-09T21:44:11+00:00

- Equity: $99,619.78
- Cash: $99,619.78
- Week P&L: $0.00 (0.00%)
- Drawdown from HWM ($99,619.78): 0.00%
- Previous weekly run: never

### Positions

None. Account is 100% cash.

### Open Orders

None.

### Paper-Only Verification

- TRADING_MODE: paper ✓
- LIVE_TRADING_CONFIRMED: false ✓
- DRY_RUN: true ✓
- No live orders submitted this week.

### Crypto / Options / Short Position Check

- No crypto positions detected.
- No options positions detected.
- No short positions detected.
- Alpaca account `shorting_enabled=true` (broker default), but strategy has no short positions. No action required.

### Universe Compliance

All symbols appearing in signal and trade logs (KO, WMT, PEP, GOOGL, MRK, AMZN, XOM, NVDA, LLY, AVGO, AMD) are present in `config/universe.json`. No unexpected symbols observed.

### Market Data Update Status

- Stage 1 ran 3 times on 2026-05-09.
- All runs fetched 30/30 symbols successfully.
- Bars age: 24h at each run (market was closed — expected for end-of-day/after-hours runs).
- No stale data blocks triggered.
- Data hashes: first run `b3f857e47e27db5f` (0 eligible — see note), subsequent runs `8d8159954c59ae83` (14 eligible).

**Note — First-run eligibility anomaly:** The first data fetch (21:23 UTC) produced 0/28 scored candidates and fell back to BIL 90%. The second run (21:24 UTC) with a new data hash produced 14/28 eligible with full equity targets. This suggests the first run may have fetched incomplete or not-yet-computed data. The system correctly recovered on the next run. No intervention required, but worth monitoring for pattern.

### Trade Plan Status

- Generated on 2026-05-09.
- 11 equity targets + 10% cash reserve.
- Target names: KO (12.32%), WMT (11.31%), PEP (10.44%), GOOGL (8.81%), MRK (8.01%), AMZN (7.99%), XOM (7.14%), NVDA (6.74%), LLY (6.62%), AVGO (6.40%), AMD (4.23%).
- All symbols within sector caps (max 3 per sector).
- Sector distribution: Consumer Staples ×3 (KO/WMT/PEP), Communication Services ×2 (GOOGL), Healthcare ×2 (MRK/LLY), Energy ×1 (XOM), Technology ×3 (NVDA/AVGO/AMD), Consumer Discretionary ×1 (AMZN).

### Trade Execution Status

- Stage 2 ran 2 times on 2026-05-09 (both DRY_RUN).
- Orders submitted (live): 0
- DRY_RUN orders: 3 (PEP, AMZN, AMD) per run × 2 runs = 6 total DRY_RUN order events.
- Skipped (wide spread): 8 per run (KO, WMT, GOOGL, MRK, XOM, NVDA, LLY, AVGO).
- Errors: 0.

### Orders Submitted This Week

- Live orders submitted: **0**
- DRY_RUN orders (would-be): 3 per run (PEP, AMZN, AMD)
- Total DRY_RUN execution events: 6

### Duplicate Order Issues

None detected.

### Stale Data Issues

None triggered. Bars age 24h is expected for after-hours runs while market is closed.

### Spread / Risk Blocks

- **Wide-spread blocks (8 symbols):** KO, WMT, GOOGL, MRK, XOM, NVDA, LLY, AVGO.
- These blocks occurred because market was closed at execution time; spreads are artificially wide during off-hours.
- Only PEP, AMZN, and AMD passed the spread check (max_spread_bps=100) and proceeded to DRY_RUN.
- No concern for paper purposes — next live-market execution window should clear most spread blocks.

### Failed Routines

None. All Stage 1, Stage 2, position monitor, and daily summary runs completed without errors.

### Git / Push Issues

None observed.

### Drawdown / Daily Loss Lockout Status

- Drawdown from HWM: 0.00%
- HWM: $99,619.78 (set 2026-05-09)
- Max drawdown limit: 20% — not approached.
- Daily loss: +$72.21 (gain) — daily loss lockout not triggered.
- System not paused.

### Safe to Continue Paper Testing

**Yes.** All safety guards are active. No live orders were placed. No unexpected positions, symbols, or account blocks. The wide-spread blocks during off-hours are expected behavior. The first-run eligibility anomaly self-corrected. Paper testing can continue.

---
