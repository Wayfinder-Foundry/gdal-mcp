# GDAL MCP

GDAL MCP is an open‑source server implementing the Model Context Protocol (MCP). It wraps the command‑line tools from the Geospatial Data Abstraction Library (GDAL) and exposes them as MCP tools so AI agents can perform geospatial operations in a safe, user‑approved manner.

## Features

- Exposes GDAL utilities such as `gdalinfo`, `gdal_translate`, `gdalwarp`, `gdalbuildvrt`, `gdal_rasterize`, `gdal2xyz`, `gdal_merge` and `gdal_polygonize` as MCP tools.
- Uses JSON‑RPC 2.0 for communication.
- Human‑in‑the‑loop confirmation for every tool execution.
- Modular, extensible design with Python wrappers for each tool.
- Supports returning output files as resources.

## Installation

### Prerequisites

- Python 3.9 or later.
- GDAL installed on your system (e.g., `sudo apt install gdal-bin libgdal-dev`).
- The GDAL Python bindings (`pip install gdal`).

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/JordanGunn/gdal-mcp.git
   cd gdal-mcp
   ```

2. Install dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Start the server using Uvicorn:

   ```bash
   uvicorn src.server:app --host 0.0.0.0 --port 8000
   ```

   The MCP server will listen for JSON‑RPC requests at `http://localhost:8000/jsonrpc`.

> **Note:** Many existing MCP servers are distributed via `npx` or `uv/uvx` packages for Node.js or Deno. This project uses a Python/ASGI stack for easy deployment with FastAPI and Uvicorn.

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

To run the server with this configuration, set the environment variable `GDAL_MCP_CONFIG` to the path of your JSON file before starting Uvicorn.

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

For each tool, consult [`gdal_mcp_design.md`](gdal_mcp_design.md) for JSON schema definitions and sample usage.

### Example usage

To list the tools:

```bash
curl -X POST http://localhost:8000/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}'
```

To request a `gdalinfo` call:

```bash
# Prepare a JSON-RPC request
cat > request.json <<'EOF'
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "gdalinfo",
    "input": { "dataset": "/data/datasets/my.tif", "json": true }
  },
  "id": 2
}
EOF

curl -X POST http://localhost:8000/jsonrpc \
  -H "Content-Type: application/json" \
  -d @request.json
```

The server will ask for human confirmation before executing the command. Once approved, it returns the report or a resource URI.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing, reporting bugs, and running tests.

## Code of Conduct

Please note that this project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- GDAL – https://gdal.org
- Model Context Protocol – thanks to the MCP community for developing the specification.
