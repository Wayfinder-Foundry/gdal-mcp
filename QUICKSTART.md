# GDAL MCP Quickstart

This guide shows how to run the Python-native GDAL MCP server and connect it to an MCP client like Claude Desktop or Cascade.

## Installation Methods

### Method 1: uvx (Recommended)

**Once published to PyPI:**
```bash
# Install and run via uvx (no local installation required)
uvx --from gdal-mcp gdal --transport stdio
```

**During development (from local wheel):**
```bash
# Build the wheel
uv build

# Run from local wheel
uvx --from dist/gdal_mcp-0.0.1-py3-none-any.whl gdal --transport stdio
```

### Method 2: Docker

```bash
# Build the Docker image
docker build -t gdal-mcp .

# Run with stdio transport (for MCP clients)
docker run -i gdal --transport stdio

# Run with HTTP transport (for testing)
docker run -p 8000:8000 gdal --transport http --port 8000
```

### Method 3: Local Development with uv

```bash
# Clone the repository
git clone https://github.com/JordanGunn/gdal-mcp.git
cd gdal-mcp

# Install with uv
uv sync

# Run the server
uv run gdal --transport stdio
```

## Workspace Configuration

**IMPORTANT:** GDAL MCP uses workspace scoping for security (ADR-0022). You must configure `GDAL_MCP_WORKSPACES` to allow file access.

```bash
# Set allowed workspace directories (colon-separated on Linux/macOS)
export GDAL_MCP_WORKSPACES="/path/to/data:/another/path/to/rasters"

# Windows (semicolon-separated)
set GDAL_MCP_WORKSPACES="C:\data;C:\rasters"
```

Without this configuration, the server will reject all file operations for security.

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
        "gdal",
        "gdal",
        "--transport",
        "stdio"
      ],
      "env": {
        "GDAL_MCP_WORKSPACES": "/path/to/your/geospatial/data"
      }
    }
  }
}
```

**For local development (before PyPI publish):**
```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "/home/user/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "/path/to/gdal-mcp/dist/gdal_mcp-0.0.1-py3-none-any.whl",
        "gdal",
        "--transport",
        "stdio"
      ],
      "env": {
        "GDAL_MCP_WORKSPACES": "/path/to/your/geospatial/data"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

4. **Test the connection**:
   - Open Claude Desktop
   - Look for the MCP server indicator (🔌 icon)
   - Try a command like: "Use the raster_info tool to inspect this GeoTIFF: /path/to/file.tif"

## Connecting to Cascade AI

For Cascade (Windsurf IDE), configure in `~/.codeium/mcp_config.json`:

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "/home/user/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "/path/to/gdal-mcp/dist/gdal_mcp-0.0.1-py3-none-any.whl",
        "gdal"
      ],
      "env": {
        "GDAL_MCP_WORKSPACES": "/path/to/your/geospatial/data"
      }
    }
  }
}
```

**Note:** Use `uv run --with <wheel-path>` instead of `uvx` for local development to avoid caching issues.

## Available Tools

### Raster Tools

#### 1. `raster_info` - Inspect Raster Metadata

Get comprehensive metadata about a raster file:

```
Natural language: "Show me the metadata for dem.tif"

Tool call:
{
  "uri": "/data/dem.tif"
}

Output: CRS, bounds, dimensions, bands, data type, nodata value, etc.
```

#### 2. `raster_convert` - Convert Raster Formats

Convert to Cloud-Optimized GeoTIFF with compression:

```
Natural language: "Convert landsat.tif to Cloud-Optimized GeoTIFF with deflate compression"

Tool call:
{
  "uri": "/data/landsat.tif",
  "output": "/data/landsat_cog.tif",
  "options": {
    "driver": "COG",
    "compression": "deflate",
    "overviews": [2, 4, 8, 16]
  }
}
```

#### 3. `raster_reproject` - Reproject Rasters

Reproject to Web Mercator (EPSG:3857):

```
Natural language: "Reproject dem.tif to Web Mercator using cubic resampling"

Tool call:
{
  "uri": "/data/dem.tif",
  "output": "/data/dem_webmercator.tif",
  "params": {
    "dst_crs": "EPSG:3857",
    "resampling": "cubic"
  }
}
```

**Note:** Resampling method is **required** (ADR-0011). Choose:
- `nearest`: For categorical data (land cover, classification)
- `bilinear` or `cubic`: For continuous data (elevation, temperature)

#### 4. `raster_stats` - Compute Statistics

Get comprehensive statistics for bands:

```
Natural language: "Compute statistics with histogram for landsat.tif band 1"

Tool call:
{
  "uri": "/data/landsat.tif",
  "params": {
    "bands": [1],
    "include_histogram": true,
    "percentiles": [10, 25, 50, 75, 90]
  }
}

Output: min, max, mean, std, median, percentiles, histogram
```

### Vector Tools

#### 5. `vector_info` - Inspect Vector Metadata

Get metadata about vector datasets:

```
Natural language: "Show me information about parcels.shp"

Tool call:
{
  "uri": "/data/parcels.shp"
}

Output: driver, CRS, geometry types, feature count, fields, bounds
```

## Example Workflows

### 1. Inspect and Convert a Raster

```
User: "I have a GeoTIFF at /data/aerial.tif. Show me its metadata and convert it to a Cloud-Optimized GeoTIFF."

AI uses:
1. raster_info - Get metadata
2. raster_convert - Convert to COG with compression and overviews
```

### 2. Reproject and Analyze a DEM

```
User: "Reproject /data/dem.tif to UTM Zone 10N and compute elevation statistics."

AI uses:
1. raster_reproject - Reproject to EPSG:32610 (UTM 10N)
2. raster_stats - Compute min/max/mean elevation with percentiles
```

### 3. Multi-Band Satellite Analysis

```
User: "For landsat.tif, show me statistics for bands 1-3 with histograms."

AI uses:
raster_stats with bands=[1,2,3], include_histogram=true
Returns statistics and histograms for each band
```

## Troubleshooting

### "Access denied: Path outside allowed workspaces"

**Solution:** Configure `GDAL_MCP_WORKSPACES` environment variable:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export GDAL_MCP_WORKSPACES="/path/to/data"

# Or set in MCP client config (see examples above)
```

### "Tool not found" or tools have dots (raster.info)

**Solution:** Ensure you're using the latest version. Tool names changed from dots to underscores (v0.1.0+):
- OLD: `raster.info` ❌
- NEW: `raster_info` ✅

Rebuild the wheel or reinstall:
```bash
uv build
uvx --from dist/gdal_mcp-0.0.1-py3-none-any.whl gdal-mcp
```

### Server not connecting to MCP client

**Checklist:**
1. ✅ Server runs successfully with `--help` flag
2. ✅ `GDAL_MCP_WORKSPACES` is configured
3. ✅ MCP client config points to correct wheel path
4. ✅ MCP client restarted after config changes
5. ✅ Using `uv run --with` for local dev (not `uvx`)

**Test server manually:**
```bash
# Should show server initialization
uv run gdal --transport stdio
```

## Next Steps

- Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute tools or features
- Review [docs/ADR/](docs/ADR/) for architecture decisions
- Check [docs/design/](docs/design/) for design documentation
- See [.github/workflows/README.md](../.github/workflows/README.md) for CI/CD info

## Resources

- **Repository**: https://github.com/JordanGunn/gdal-mcp
- **Issues**: https://github.com/JordanGunn/gdal-mcp/issues
- **FastMCP Docs**: https://github.com/jlowin/fastmcp
- **MCP Specification**: https://modelcontextprotocol.io/
