#!/usr/bin/env bash
set -euo pipefail

HOST=${HOST:-http://localhost:8000}
ID=${ID:-1}

# List tools
curl -sS "$HOST/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"list","method":"tools/list","params":{}}' | jq .

# Optionally render the MVP prompt
curl -sS "$HOST/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc":"2.0","id":"prompt","method":"prompts/get",
    "params":{"name":"gdal_task","arguments":{"goal":"Inspect a GeoTIFF and convert to COG","input_path":"test/data/sample.tif","output_path":"out.tif"}}
  }' | jq .

# Example: info call (set DATASET env var to override)
DATASET=${DATASET:-test/data/sample.tif}
curl -sS "$HOST/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc":"2.0","id":"info","method":"tools/call",
    "params":{"name":"info","arguments":{"path":"'"$DATASET"'","format":"json"}}
  }'

# Example: convert call (no-op if GDAL missing; ensure output path is writable)
OUT=${OUT:-out.tif}
curl -sS "$HOST/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc":"2.0","id":"convert","method":"tools/call",
    "params":{"name":"convert","arguments":{"input":"'"$DATASET"'","output":"'"$OUT"'","output_format":"GTiff"}}
  }' | jq .
