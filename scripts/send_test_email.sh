#!/usr/bin/env bash
#
# Inject a test email into the running app, simulating an inbound email.
#
# Interactive:   ./scripts/send_test_email.sh
# With args:     ./scripts/send_test_email.sh "dispatch@partner.com" "orders@interview.test" "Delivery update ORD-12345" "Order ORD-12345 is out for delivery."
#
# Only needs bash + curl. Talks to the app on localhost:8000.

set -euo pipefail

URL="${URL:-http://localhost:8000/inbound/email/}"

FROM="${1:-}"
TO="${2:-}"
SUBJECT="${3:-}"
BODY="${4:-}"

[ -z "$FROM" ] && read -r -p "From:    " FROM
[ -z "$TO" ] && read -r -p "To:      " TO
[ -z "$SUBJECT" ] && read -r -p "Subject: " SUBJECT
[ -z "$BODY" ] && read -r -p "Body:    " BODY

# Minimal JSON string escaping (backslash, double-quote, newline, tab).
json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
}

PAYLOAD=$(printf '{"from":"%s","to":"%s","subject":"%s","body":"%s"}' \
  "$(json_escape "$FROM")" "$(json_escape "$TO")" "$(json_escape "$SUBJECT")" "$(json_escape "$BODY")")

echo "POST $URL"
echo "  $PAYLOAD"
echo
curl -sS -X POST "$URL" -H "Content-Type: application/json" -d "$PAYLOAD"
echo
