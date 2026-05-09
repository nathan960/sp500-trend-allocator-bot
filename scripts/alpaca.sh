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

cmd="${1:-}"
case "$cmd" in
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
  assets)
    curl -sS "${HDR[@]}" "$BASE/v2/assets?asset_class=us_equity&status=active"
    ;;
  *)
    echo "Usage: $0 account|positions|orders [open|closed|all]|assets" >&2
    exit 2
    ;;
esac
