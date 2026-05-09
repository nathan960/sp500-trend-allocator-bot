#!/usr/bin/env bash
set -euo pipefail

if [[ -f ".env" ]]; then
  set -a
  source .env
  set +a
fi

msg="${1:-}"
provider="${NOTIFY_PROVIDER:-discord}"
mkdir -p memory

if [[ -z "$msg" ]]; then
  echo "notify.sh requires a message" >&2
  exit 2
fi

case "$provider" in
  discord)
    if [[ -n "${DISCORD_WEBHOOK_URL:-}" ]]; then
      python3 -c 'import os,requests,sys; requests.post(os.environ["DISCORD_WEBHOOK_URL"], json={"content": sys.argv[1][:1900]}, timeout=10)' "$msg"
    else
      printf "\n\n## Notification fallback\n%s\n" "$msg" >> memory/NOTIFICATION-FALLBACK.md
    fi
    ;;
  slack)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
      python3 -c 'import os,requests,sys; requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": sys.argv[1][:3000]}, timeout=10)' "$msg"
    else
      printf "\n\n## Notification fallback\n%s\n" "$msg" >> memory/NOTIFICATION-FALLBACK.md
    fi
    ;;
  *)
    printf "\n\n## Notification fallback\n%s\n" "$msg" >> memory/NOTIFICATION-FALLBACK.md
    ;;
esac
