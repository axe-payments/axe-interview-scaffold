#!/usr/bin/env bash
#
# Smoke test: place a real outbound call directly, bypassing the engine.
# Use this to confirm your Vapi credentials work before you start building.
#
# Interactive:  ./scripts/test_call.sh
# With args:    ./scripts/test_call.sh "+14155551234"
#
# Only needs bash + curl. Talks to the app on localhost:8000.

set -euo pipefail

URL="${URL:-http://localhost:8000/debug/call/}"

TARGET="${1:-}"
[ -z "$TARGET" ] && read -r -p "Phone to call (E.164, e.g. +14155551234): " TARGET

PAYLOAD=$(printf '{"target_number":"%s","variables":{"contact_name":"Test Caller"}}' "$TARGET")

echo "POST $URL"
echo "  $PAYLOAD"
echo
curl -sS -X POST "$URL" -H "Content-Type: application/json" -d "$PAYLOAD"
echo
