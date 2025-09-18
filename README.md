# GDAL MCP

GDAL MCP is an open‑source server implementing the Model Context Protocol (MCP). It wraps the command‑line tools from the Geospatial Data Abstraction Library (GDAL) and exposes them as MCP tools so AI agents can perform geospatial operations in a safe, user‑approved manner.

## Features

- Exposes core GDAL utilities such as `gdalinfo`, `gdal_translate`, `gdalwarp`, and `gdalbuildvrt` as MCP tools.
- Uses JSON‑RPC 2.0 for communication.
- Human‑in‑the‑loop confirmation for every tool execution.
- Modular, extensible design with Python wrappers for each tool.
 

## Installation

### Prerequisites

- Python 3.10 or later.
- GDAL CLI installed on your system (e.g., Homebrew on macOS: `brew install gdal`, or conda-forge).
  - The server shells out to the GDAL binaries; Python GDAL bindings are not required.

### Steps

1. Clone this repository:

   ```bash
   git clone https://github.com/JordanGunn/gdal-mcp.git
   cd gdal-mcp
   ```

2. Install dependencies (recommended with [uv](https://docs.astral.sh/uv/)):

   Recommended: use [uv](https://docs.astral.sh/uv/) to manage the Python environment and install MCP and GDAL dependencies:

  ```bash
  uv pip install -e ".[dev]"
  ```

  Alternatively with pip:

  ```bash
  python3 -m pip install -e ".[dev]"
  ```

3. Run the MCP server (stdio transport):

   Using the console script installed via this package:

  ```bash
  uv run gdal-mcp-server
  ```

   Or with Python module execution:

  ```bash
  uv run python -m server.gdal_tools
  ```

> **Note:** The server uses the GDAL command-line tools. If the VS Code extension host doesn't inherit your shell PATH, set `GDAL_BIN` to the directory containing GDAL binaries (e.g., `/opt/homebrew/bin`) in your MCP configuration for the `gdal` server.


## MCP tools

The server exposes the following tools via `tools/list` and `tools/call`:

| Tool name | Description |
| --- | --- |
| `gdalinfo` | Prints summary information about a raster dataset (metadata, geolocation, statistics). |
| `gdal_translate` | Converts raster data between formats, and can subset, resample or rescale pixels. |
| `gdalwarp` | Reprojects and warps raster images; can mosaic multiple inputs and apply ground control points. |
| `gdalbuildvrt` | Builds a virtual mosaic (VRT) from a list of input rasters. |
 

For each tool, consult [`gdal_mcp_design.md`](gdal_mcp_design.md) for JSON schema definitions and sample usage.

### MCP client usage

#### Transports

| Transport | How to run | Notes |
|-----------|------------|-------|
| stdio | `uv run gdal-mcp-server` | Best for editor integrations / MCP clients spawning a subprocess |

The server exposes tools via `tools/list` and `tools/call` over stdio. Use an MCP-compatible client (e.g., VS Code MCP extension) to interact.

### VS Code MCP configuration

Add to your user `mcp.json`:

```jsonc
{
  "servers": {
    "gdal": {
      "command": "/absolute/path/to/your/venv/bin/gdal-mcp-server",
      "transport": "stdio",
      "workingDirectory": "/absolute/path/to/gdal-mcp",
      "env": {
        "GDAL_BIN": "path/to/gdal/bin"  // Optional: ensure GDAL is in the PATH
      }
    }
  }
}
```

If PATH is already correct and gdal is included, `GDAL_BIN` is optional.

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing, reporting bugs, and running tests.

## Code of Conduct

Please note that this project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- GDAL – https://gdal.org
- Model Context Protocol – thanks to the MCP community for developing the specification.
