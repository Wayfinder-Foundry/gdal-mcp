# GDAL MCP Quickstart

This guide shows how to run the Python-native GDAL MCP server and connect it to an MCP client like Claude Desktop.

## Installation Methods

### Method 1: uvx (Recommended for Development)

```bash
# Install and run via uvx (no installation required)
uvx --from . gdal-mcp --transport stdio
```

### Method 2: Docker

```bash
# Build the Docker image
docker build -t gdal-mcp .

# Run with stdio transport (for MCP clients)
docker run -i gdal-mcp --transport stdio

# Run with HTTP transport (for testing)
docker run -p 8000:8000 gdal-mcp --transport http --port 8000
```

### Method 3: Local Installation

```bash
# Install with uv
uv pip install -e .

# Or with pip
pip install -e .

# Run the server
gdal-mcp --transport stdio
```

## Connecting to Claude Desktop

1. **Locate your Claude Desktop config file**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add the MCP server configuration**:

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "gdal-mcp",
        "gdal-mcp",
        "--transport",
        "stdio"
      ],
      "env": {
        "GDAL_CACHEMAX": "512",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.tiff,.vrt,.geojson,.json,.shp"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test the connection**:
   - Open Claude Desktop
   - Look for the MCP server indicator (🔌 icon)
   - Try a command like: "Use the raster.info tool to inspect this GeoTIFF: /path/to/file.tif"

## Available Tools

### Raster Tools

- **raster.info** - Inspect raster metadata (CRS, bounds, transform, bands, nodata)
- **raster.stats** - Compute statistics (min/max/mean/std/percentiles/histogram)
- **raster.convert** - Convert formats with compression, tiling, and overviews
- **raster.reproject** - Reproject to new CRS with explicit resampling

### Vector Tools

- **vector.info** - Inspect vector metadata (CRS, geometry types, fields, bounds)

## Example Usage

### Inspect a raster
```python
# Via MCP client
"Use raster.info to inspect example.tif"

# Returns: RasterInfo with driver, CRS, bounds, transform, etc.
```

### Compute raster statistics
```python
# Via MCP client
"Use raster.stats on example.tif with histogram enabled"

# Returns: RasterStatsResult with min/max/mean/std/percentiles/histogram
```

### Convert with compression
```python
# Via MCP client
"Use raster.convert to convert input.tif to output_cog.tif with driver=COG and compression=deflate"

# Returns: ConversionResult with ResourceRef to output file
```

### Reproject to Web Mercator
```python
# Via MCP client
"Use raster.reproject to reproject input.tif to EPSG:3857 with bilinear resampling, save to output.tif"

# Returns: ReprojectionResult with ResourceRef and metadata
```

## Testing the Server

### Test with HTTP transport

```bash
# Start server on port 8000
gdal-mcp --transport http --port 8000

# In another terminal, test the tools endpoint
curl http://localhost:8000/tools

# Test a tool call
curl -X POST http://localhost:8000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "raster.info",
    "arguments": {
      "uri": "/path/to/raster.tif"
    }
  }'
```

### Test with stdio (for debugging)

```bash
# Run and provide JSON-RPC input via stdin
gdal-mcp --transport stdio
```

## Troubleshooting

**GDAL not found**: Ensure GDAL libraries are installed
- Ubuntu/Debian: `sudo apt-get install gdal-bin libgdal-dev`
- macOS: `brew install gdal`
- Windows: Install OSGeo4W or use Docker

**Python dependencies missing**: Install dev dependencies
```bash
uv pip install -e ".[dev]"
```

**MCP connection failed**: Check Claude Desktop logs
- macOS: `~/Library/Logs/Claude/mcp*.log`
- Windows: `%APPDATA%\Claude\logs\mcp*.log`

**Permission errors**: Ensure the server has read access to input files and write access to output directories

## Next Steps

- See [README.md](README.md) for full documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) for development guide
- See [docs/](docs/) for architecture and ADRs
