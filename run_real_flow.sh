#!/usr/bin/env bash
set -euo pipefail

TICKET_ID="${1:-AS360-340}"
USERNAME="${2:-}"
PASSWORD="${3:-}"

if [[ -n "$USERNAME" && -n "$PASSWORD" ]]; then
  uv run python main.py --ticket "$TICKET_ID" -u "$USERNAME" -p "$PASSWORD"
else
  uv run python main.py --ticket "$TICKET_ID"
fi
