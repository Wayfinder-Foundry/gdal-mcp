#!/usr/bin/env bash
set -euo pipefail
BASE_URL=${1:-http://127.0.0.1:8000}
ACCEPT='application/json, text/event-stream'

json() { jq -r "$1" ; }

init_payload='{"jsonrpc":"2.0","id":"1","method":"initialize","params":{"clientInfo":{"name":"curl-client","version":"0.1"},"capabilities":{}}}'

echo "[*] Initializing session..." >&2
init_resp=$(curl -s -X POST "$BASE_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H "Accept: $ACCEPT" \
  -d "$init_payload")

echo "$init_resp" | jq . >/dev/null || { echo "Initialization failed (no JSON)" >&2; exit 1; }
SESSION_ID=$(echo "$init_resp" | jq -r '.result.sessionId // empty')
if [ -z "$SESSION_ID" ]; then
  echo "Could not extract sessionId from initialize response:" >&2
  echo "$init_resp" >&2
  exit 1
fi

echo "[+] Session ID: $SESSION_ID" >&2

# Send notifications/initialized (fire-and-forget)
notify_payload='{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

curl -s -X POST "$BASE_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H "Accept: $ACCEPT" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "$notify_payload" >/dev/null || true

echo "[*] Listing tools..." >&2
list_payload='{"jsonrpc":"2.0","id":"2","method":"tools/list","params":{}}'
list_resp=$(curl -s -X POST "$BASE_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H "Accept: $ACCEPT" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "$list_payload")

echo "$list_resp" | jq . || echo "$list_resp"

echo "[*] Calling gdalinfo on test_data/sample.tif" >&2
call_payload='{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"gdalinfo","arguments":{"dataset":"test_data/sample.tif","json_output":false}}}'
call_resp=$(curl -s -X POST "$BASE_URL/mcp" \
  -H 'Content-Type: application/json' \
  -H "Accept: $ACCEPT" \
  -H "mcp-session-id: $SESSION_ID" \
  -d "$call_payload")

echo "$call_resp" | jq . || echo "$call_resp"

echo "Done." >&2
