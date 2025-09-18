---
type: product_context
title: GDAL MCP Overview
tags: [gdal, mcp, server, docs]
---

# GDAL MCP

GDAL MCP is an open‑source server implementing the Model Context Protocol (MCP). It wraps the command‑line tools from the Geospatial Data Abstraction Library (GDAL) and exposes them as MCP tools so AI agents can perform geospatial operations in a safe, user‑approved manner.

## Features

- Implements the GDAL 3.11 unified CLI as MCP tools (initial set): `info`, `convert`, `reproject` (raster).
- JSON‑RPC 2.0 communication via FastMCP (stdio or HTTP transport).
- Human‑in‑the‑loop confirmation for every tool execution.
- Modular wrappers with typed signatures and clear error surfacing.
- File‑producing tools publish results as `file://` resources.

## Installation

### Prerequisites

- Python 3.10+.
- GDAL 3.11+ CLI available on PATH (unified `gdal` command). For Debian/Ubuntu: `sudo apt install gdal-bin`.

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/JordanGunn/gdal-mcp.git
   cd gdal-mcp
   ```

2. Install deps (recommended: [uv](https://docs.astral.sh/uv/)):

   ```bash
   uv sync
   ```

3. Run the server (stdio or HTTP):

   ```bash
   # stdio (typical for editor integrations)
   uv run gdal-mcp serve --transport stdio

   # HTTP
   uv run gdal-mcp serve --transport http --port 8000
   ```

   Or via Python module:

   ```bash
   uv run python -m gdal_mcp serve --transport stdio
   ```

   The server listens for JSON‑RPC requests implementing the Model Context Protocol.

> **Note:** Many MCP servers are distributed via `npx` or `uv/uvx` packages for Node.js or Deno. This project now uses the MCP Python SDK and `uv` for dependency management and execution.
ployment with FastAPI and Uvicorn.

## Configuration

You can customise server behaviour through a simple JSON configuration file. Create a `config.json` in the project root:

```json
{
  "workdir": "/tmp/gdal-mcp-workdir",
  "whitelist": ["/data/datasets"],
  "max_timeout": 3600,
  "port": 8000
}
```

- `workdir` – directory where output files will be stored.
- `whitelist` – list of directories that the server is allowed to read from.
- `max_timeout` – maximum execution time (seconds) for GDAL commands.
- `port` – TCP port for the server.

To run the server with this configuration, set the environment variable `GDAL_MCP_CONFIG` to the path of your JSON file before starting .

## MCP tools

The server exposes the following tools via `tools/list` and `tools/call`:

| Tool name | Description |
| --- | --- |
| `gdalinfo` | Prints summary information about a raster dataset (metadata, geolocation, statistics). |
| `gdal_translate` | Converts raster data between formats, and can subset, resample or rescale pixels. |
| `gdalwarp` | Reprojects and warps raster images; can mosaic multiple inputs and apply ground control points. |
| `gdalbuildvrt` | Builds a virtual mosaic (VRT) from a list of input rasters. |
| `gdal_rasterize` | Burns vector geometries into raster band(s). |
| `gdal2xyz` | Converts a raster dataset into x/y/z points, supporting multiple bands and nodata handling. |
| `gdal_merge` | Mosaics a set of images that share the same coordinate system and number of bands. |
| `gdal_polygonize` | Creates vector polygons from connected regions of pixels with the same value. |

For detailed JSON Schemas, architecture notes, and testing guidance see [`docs/design/`](docs/design/index.md).

### HTTP / JSON‑RPC Usage (FastMCP HTTP)

The FastMCP streamable HTTP transport mounts a **single endpoint** (default: `/mcp`) that handles all JSON‑RPC 2.0 requests. In stateless mode (enabled in this project) you do **not** need an initialization handshake or a session header for quick tool invocations.

#### Transports

| Transport | How to run | Notes |
|-----------|------------|-------|
| stdio | `uv run gdal-mcp serve --transport stdio` | Best for editor integrations |
| http | `uv run gdal-mcp serve --transport http --port 8000` | Single `/mcp` endpoint; supports streaming + JSON responses |

#### Accept Header

The streamable HTTP transport negotiates streaming; we keep `json_response=True` but some versions still expect you to advertise support for both content types. Include:

```
Accept: application/json, text/event-stream
```

#### Stateless vs Session Mode

We initialize FastMCP with `stateless_http=True`, so each request is independent and you can omit `mcp-session-id`. If you disable stateless mode later, you must:
1. Send `initialize` with a `mcp-session-id` header.
2. (Optionally) send `notifications/initialized`.
3. Then issue `tools/list` / `tools/call` with the same session ID.

#### List Tools

```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'
```

#### Call `info`

```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "info",
      "arguments": { "path": "test/data/sample.tif", "format": "json" }
    }
  }'
```

#### Call `convert`

```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "convert",
      "arguments": { "input": "test/data/sample.tif", "output": "out.tif", "output_format": "GTiff" }

#### Call `reproject`

```bash
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{
    "jsonrpc": "2.0",
    "id": "4",
    "method": "tools/call",
    "params": {
      "name": "reproject",
      "arguments": { "input": "test/data/sample.tif", "output": "reproj.tif", "dst_crs": "EPSG:4326" }
    }
  }'
```
    }
  }'
```

#### Session Mode Example (if you disable `stateless_http`)

```bash
# 1. Initialize
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'mcp-session-id: demo-1' \
  -d '{
    "jsonrpc":"2.0",
    "id":"init-1",
    "method":"initialize",
    "params": { "protocolVersion":"2024-11-05", "capabilities": {"tools":{}}, "clientInfo":{"name":"curl","version":"0.0.1"}}
  }'

# 2. List tools in the same session
curl -X POST http://localhost:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'mcp-session-id: demo-1' \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/list","params":{}}'
```

#### Common Errors

| Message | Cause | Fix |
|---------|-------|-----|
| Not Acceptable: Client must accept both application/json and text/event-stream | Missing or incomplete Accept header | Add `-H 'Accept: application/json, text/event-stream'` |
| Missing session ID | Server running in stateful mode | Add `mcp-session-id` header or enable `stateless_http=True` |
| No valid session ID provided | Invalid / missing session header in stateful mode | Ensure consistent, non-empty `mcp-session-id` |
| Command not found: gdalinfo | GDAL binaries not in PATH | Install GDAL (e.g. `brew install gdal`) |

### Resources

File‑producing tools return a `resource_uri` (`file://...`) and register it with the server so clients can list/read it via the MCP resources API.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing, reporting bugs, and running tests.

## Code of Conduct

Please note that this project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- GDAL – https://gdal.org
- Model Context Protocol – thanks to the MCP community for developing the specification.
