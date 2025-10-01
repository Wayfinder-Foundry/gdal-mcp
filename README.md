# GDAL MCP

**Python-native geospatial tools for AI agents via Model Context Protocol**

GDAL MCP is an open-source MCP server that exposes powerful geospatial operations through FastMCP. Instead of shelling out to GDAL CLI, it uses Python-native libraries (Rasterio, PyProj, pyogrio, Shapely) for direct, type-safe geospatial processing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-15%2F15%20passing-brightgreen.svg)](#testing)

## 🚀 Features

- **Python-Native Stack**: Uses Rasterio, PyProj, pyogrio, and Shapely—no CLI shelling
- **5 Core Tools**: Raster info/convert/reproject/stats + vector info (MVP per ADR-0005)
- **Type-Safe**: Pydantic models for all inputs/outputs with JSON schema auto-generation
- **FastMCP Framework**: JSON-RPC 2.0 over stdio or HTTP transport
- **ADR-Compliant**: Explicit resampling, structured outputs, resource references
- **Comprehensive Tests**: 15/15 tests passing with pytest fixtures
- **Docker Ready**: Multi-stage build with GDAL 3.8.0 base

## 📦 Installation

### Method 1: uvx (Recommended)

```bash
# Run directly without installation
uvx --from gdal-mcp gdal-mcp --transport stdio
```

### Method 2: Docker

```bash
# Build and run
docker build -t gdal-mcp .
docker run -i gdal-mcp --transport stdio
```

### Method 3: Local Development

```bash
# Clone and install
git clone https://github.com/JordanGunn/gdal-mcp.git
cd gdal-mcp
uv sync
uv run gdal-mcp --transport stdio
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 🔧 Available Tools

### Raster Tools

#### `raster.info`
Inspect raster metadata using Rasterio.

**Input**: `uri` (str), optional `band` (int)

**Output**: `RasterInfo` with:
- Driver, CRS, bounds, transform
- Width, height, band count, dtype
- NoData value, overview levels, tags

**Example**: Get metadata for a GeoTIFF
```python
{
  "uri": "/data/example.tif",
  "band": 1
}
```

#### `raster.convert`
Convert raster formats with compression, tiling, and overviews.

**Input**: `uri` (str), `output` (str), optional `options` (ConversionOptions)

**Options**:
- `driver`: Output format (GTiff, COG, PNG, JPEG, etc.)
- `compression`: lzw, deflate, zstd, jpeg, packbits, none
- `tiled`: Boolean (default True)
- `blockxsize/blockysize`: Tile dimensions (default 256)
- `overviews`: List of levels (e.g., [2, 4, 8, 16])
- `creation_options`: Dict of additional driver options

**Output**: `ConversionResult` with ResourceRef and file size

**Example**: Convert to COG with compression
```python
{
  "uri": "/data/input.tif",
  "output": "/data/output_cog.tif",
  "options": {
    "driver": "COG",
    "compression": "deflate",
    "overviews": [2, 4, 8]
  }
}
```

#### `raster.reproject`
Reproject rasters to new CRS with explicit resampling (ADR-0011).

**Input**: `uri` (str), `output` (str), `params` (ReprojectionParams)

**Params**:
- `dst_crs`: Target CRS (e.g., "EPSG:3857")
- `resampling`: **Required** - nearest, bilinear, cubic, lanczos, etc.
- `src_crs`: Optional override
- `resolution`: Optional (x_res, y_res) tuple
- `width/height`: Optional output dimensions
- `bounds`: Optional (left, bottom, right, top)
- `nodata`: Optional nodata override

**Output**: `ReprojectionResult` with ResourceRef, transform, and bounds

**Example**: Reproject to Web Mercator with bilinear resampling
```python
{
  "uri": "/data/input.tif",
  "output": "/data/reprojected.tif",
  "params": {
    "dst_crs": "EPSG:3857",
    "resampling": "bilinear"
  }
}
```

#### `raster.stats`
Compute comprehensive statistics with NumPy.

**Input**: `uri` (str), optional `params` (RasterStatsParams)

**Params**:
- `bands`: List of band indices (None = all bands)
- `include_histogram`: Boolean (default False)
- `histogram_bins`: 2-1024 bins (default 256)
- `percentiles`: List of percentiles (default [25, 50, 75])
- `sample_size`: Optional sampling for large rasters

**Output**: `RasterStatsResult` with per-band statistics:
- min, max, mean, std, median
- Percentiles (configurable)
- Valid/nodata pixel counts
- Optional histogram

**Example**: Compute stats with histogram
```python
{
  "uri": "/data/example.tif",
  "params": {
    "include_histogram": true,
    "histogram_bins": 128,
    "percentiles": [10, 50, 90]
  }
}
```

### Vector Tools

#### `vector.info`
Inspect vector metadata using pyogrio (or fiona fallback).

**Input**: `uri` (str)

**Output**: `VectorInfo` with:
- Driver, CRS, bounds
- Geometry types
- Field schema (name, type)
- Feature count

**Example**: Get metadata for a GeoJSON
```python
{
  "uri": "/data/boundaries.geojson"
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# All tests with pytest
uv run pytest test/ -v

# With coverage
uv run pytest test/ --cov=src --cov-report=term-missing

# Specific test file
uv run pytest test/test_raster_tools.py -v
```

**Current Status**: ✅ 15/15 tests passing

Test fixtures create tiny synthetic datasets (10×10 rasters, 3-feature vectors) for fast validation.

## 🔌 Connecting to Claude Desktop

See [QUICKSTART.md](QUICKSTART.md) for full instructions. Quick version:

1. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "uvx",
      "args": ["--from", "gdal-mcp", "gdal-mcp", "--transport", "stdio"],
      "env": {
        "GDAL_CACHEMAX": "512"
      }
    }
  }
}
```

2. Restart Claude Desktop
3. Test with: "Use raster.info to inspect /path/to/raster.tif"

## 🏗️ Architecture

**Python-Native Stack** (ADR-0017):
- **Rasterio** - Raster I/O and manipulation
- **PyProj** - CRS operations and transformations
- **pyogrio** - High-performance vector I/O (fiona fallback)
- **Shapely** - Geometry operations
- **NumPy** - Array operations and statistics
- **Pydantic** - Type-safe models with JSON schema

**Design Principles** (see [docs/design/](docs/design/)):
- ADR-0007: Structured outputs with Pydantic
- ADR-0011: Explicit resampling methods
- ADR-0012: Large outputs via ResourceRef
- ADR-0013: Per-request config isolation
- ADR-0017: Python-native over CLI shelling

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Setup and usage guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide
- [docs/design/](docs/design/) - Architecture and design docs
- [docs/ADR/](docs/ADR/) - Architecture Decision Records

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guide (Ruff + mypy)
- Testing requirements (pytest + fixtures)
- ADR process

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Powered by [Rasterio](https://github.com/rasterio/rasterio) and [GDAL](https://gdal.org)
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io)

## 🔮 Roadmap

**MVP Complete** ✅:
- ✅ Raster tools (info, convert, reproject, stats)
- ✅ Vector info tool
- ✅ Comprehensive tests (15/15)
- ✅ Docker deployment
- ✅ MCP client integration

**Next Steps**:
- Vector reprojection and conversion
- Spatial analysis operations
- Multi-layer support
- Benchmark suite (ADR-0015)
- Performance optimizations

---

**Status**: MVP Ready for Public Release 🚀

Built with ❤️ for the geospatial AI community.
