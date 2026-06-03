#!/usr/bin/env bash
#
# Smoke test: place a real outbound call directly, bypassing the engine.
# Use this to confirm your Vapi credentials work before you start building.
#
# Just enter a phone number to call. It uses a default agent + number (the first
# of each in app/vapi.py; see also GET /agents/ and GET /phone-numbers/).
#
# Interactive:  ./scripts/test_call.sh
# With args:    ./scripts/test_call.sh "+14155551234"
#
# Only needs bash + curl. Talks to the app on localhost:8000.

set -euo pipefail

URL="${URL:-http://localhost:8000/debug/call/}"

# Default agent + number for the smoke test (the first of each in app/vapi.py).
ASSISTANT_ID="1fd811c3-2e8d-448e-a6de-3de998a8dde6"
PHONE_NUMBER_ID="d7c73608-369e-4e2a-915b-4fb5dfb886c0"

TARGET="${1:-}"
[ -z "$TARGET" ] && read -r -p "Phone to call (E.164, e.g. +14155551234): " TARGET

PAYLOAD=$(printf '{"target_number":"%s","assistant_id":"%s","phone_number_id":"%s"}' \
  "$TARGET" "$ASSISTANT_ID" "$PHONE_NUMBER_ID")

echo "POST $URL"
echo "  $PAYLOAD"
echo
curl -sS -X POST "$URL" -H "Content-Type: application/json" -d "$PAYLOAD"
echo
