#!/usr/bin/env bash
#
# Smoke test: place a real outbound call directly, bypassing the engine.
# Use this to confirm your Vapi credentials work before you start building.
#
# You choose which agent answers and which number it calls from. Look them up:
#   curl localhost:8000/agents/          -> assistant IDs (and the {{ variables }} each expects)
#   curl localhost:8000/phone-numbers/   -> phone number IDs
# or browse http://localhost:8000/docs.
#
# Interactive:  ./scripts/test_call.sh
# With args:    ./scripts/test_call.sh "+14155551234" "<assistant_id>" "<phone_number_id>"
#
# Only needs bash + curl. Talks to the app on localhost:8000.

set -euo pipefail

URL="${URL:-http://localhost:8000/debug/call/}"

TARGET="${1:-}"
ASSISTANT_ID="${2:-}"
PHONE_NUMBER_ID="${3:-}"

[ -z "$TARGET" ] && read -r -p "Phone to call (E.164, e.g. +14155551234): " TARGET
[ -z "$ASSISTANT_ID" ] && read -r -p "Assistant ID (see GET /agents/):        " ASSISTANT_ID
[ -z "$PHONE_NUMBER_ID" ] && read -r -p "Phone number ID (see GET /phone-numbers/): " PHONE_NUMBER_ID

PAYLOAD=$(printf '{"target_number":"%s","assistant_id":"%s","phone_number_id":"%s","variables":{}}' \
  "$TARGET" "$ASSISTANT_ID" "$PHONE_NUMBER_ID")

echo "POST $URL"
echo "  $PAYLOAD"
echo
curl -sS -X POST "$URL" -H "Content-Type: application/json" -d "$PAYLOAD"
echo
