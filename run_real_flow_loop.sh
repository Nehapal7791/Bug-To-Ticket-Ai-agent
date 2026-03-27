#!/usr/bin/env bash
set -euo pipefail

TICKET_ID="${1:-AS360-340}"
USERNAME="${2:-}"
PASSWORD="${3:-}"

if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
  echo "Usage: bash run_real_flow_loop.sh <ticket_id> <username> <password>"
  exit 1
fi

while true; do
  uv run python main.py --ticket "$TICKET_ID" -u "$USERNAME" -p "$PASSWORD"
  echo
  echo "Re-run same flow? [y/N]"
  read -r answer
  if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    break
  fi
done
