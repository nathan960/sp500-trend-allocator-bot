#!/usr/bin/env bash
set -euo pipefail

if [[ -f ".env" ]]; then
  set -a
  source .env
  set +a
fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set}"

BASE="${ALPACA_BASE_URL:-https://paper-api.alpaca.markets}"
HDR=(-H "APCA-API-KEY-ID: ${ALPACA_API_KEY}" -H "APCA-API-SECRET-KEY: ${ALPACA_SECRET_KEY}" -H "Content-Type: application/json")

PYTHON="${PYTHON:-python3}"
if [[ -d ".venv" ]]; then
  PYTHON=".venv/bin/python3"
fi

cmd="${1:-}"
case "$cmd" in
  # ---- Read-only API checks ----
  account)
    curl -sS "${HDR[@]}" "$BASE/v2/account"
    ;;
  positions)
    curl -sS "${HDR[@]}" "$BASE/v2/positions"
    ;;
  orders)
    status="${2:-open}"
    curl -sS "${HDR[@]}" "$BASE/v2/orders?status=$status&limit=500"
    ;;
  clock)
    curl -sS "${HDR[@]}" "$BASE/v2/clock"
    ;;
  assets)
    curl -sS "${HDR[@]}" "$BASE/v2/assets?asset_class=us_equity&status=active"
    ;;
  # ---- Two-stage workflow ----
  signals)
    # Stage 1 only: fetch data + write trade plan (never places orders)
    export DRY_RUN=true
    export TRADING_MODE="${TRADING_MODE:-paper}"
    "$PYTHON" scripts/run_market_data_update.py
    ;;
  run)
    # Full rebalance: Stage 1 (data) → Stage 2 (execution)
    # DRY_RUN defaults to true for safety; set DRY_RUN=false to actually trade.
    export DRY_RUN="${DRY_RUN:-true}"
    export TRADING_MODE="${TRADING_MODE:-paper}"
    export LIVE_TRADING_CONFIRMED="${LIVE_TRADING_CONFIRMED:-false}"
    echo "[alpaca.sh] DRY_RUN=$DRY_RUN  TRADING_MODE=$TRADING_MODE"
    echo ""
    echo "=== Stage 1: Market Data + Signal Plan ==="
    "$PYTHON" scripts/run_market_data_update.py
    echo ""
    echo "=== Stage 2: Trade Execution ==="
    "$PYTHON" scripts/run_trade_execution.py
    echo ""
    bash scripts/notify.sh "Strategy run complete (DRY_RUN=$DRY_RUN TRADING_MODE=$TRADING_MODE)" || true
    ;;
  *)
    echo "Usage: $0 account|positions|orders [status]|clock|assets|signals|run" >&2
    echo "       DRY_RUN=false TRADING_MODE=paper $0 run   # paper trade" >&2
    exit 2
    ;;
esac
