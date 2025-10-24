# GDAL MCP

**Democratizing geospatial analysis through conversational AI**

GDAL MCP is a production-ready MCP server that exposes powerful geospatial operations through natural language interaction. Built with empathy for domain experts who need GDAL's capabilities without the CLI complexity.

**🎉 v1.0.0 Released (2025-10-24):** Complete reflection preflight system - geospatial reasoning with justified decisions!
**🚀 Milestone:** First production-ready release with epistemic governance and domain-aware tool composition.

[![CI](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.0](https://img.shields.io/badge/FastMCP-2.0-blue.svg)](https://github.com/jlowin/fastmcp)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/gdal-mcp?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/gdal-mcp)

## 🌟 Vision

**Bridging the gap between geospatial domain experts and powerful tools.**

Instead of requiring analysts to master:
- Command-line interfaces
- Python programming
- System configuration
- GDAL syntax

**Users can now ask in natural language:**
- "Show me the metadata for this raster"
- "Convert this to Cloud-Optimized GeoTIFF with compression"
- "Reproject this DEM to Web Mercator using cubic resampling"

The AI agent uses GDAL MCP under the hood - properly, safely, with production-quality code.

## 🚀 Features

### Geospatial Reasoning (v1.0.0)
- **🧠 Reflection Preflight System**: Pre-execution reasoning prompts for consequential operations
- **📝 Justified Decisions**: Intent, alternatives, choice, and confidence tracking
- **💾 Persistent Context**: Disk-based reflection store with domain-aware caching
- **🎯 Domain Awareness**: CRS selection, resampling methods, hydrology, aggregation reasoning
- **🔗 Tool Composition**: Models discover workflows through understanding + tool awareness

### Production Quality
- **✅ Type-Safe**: Full mypy strict mode compliance, Pydantic models with JSON schemas
- **🧪 Tested**: 72 passing tests with comprehensive coverage
- **🔒 Secure**: PathValidationMiddleware for workspace isolation (ADR-0022)
- **⚡ Fast**: Python-native stack (Rasterio, PyProj, pyogrio, Shapely)
- **📊 Observable**: Real-time LLM feedback during long operations (ADR-0020)

### Resources & Discovery
- **🧭 Workspace Catalog**: `catalog://workspace/{all|raster|vector}/{subpath}` for autonomous planning
- **🔍 Metadata Intelligence**: `metadata://{file}/format` for driver/format details
- **📚 Reference Library**: CRS, resampling, compression, glossary knowledge (`reference://crs/common/{coverage}`)

### Infrastructure
- **FastMCP 2.0**: Native configuration, middleware, Context API
- **CI/CD Pipeline**: GitHub Actions with quality gates, test matrix, PyPI publishing
- **ADR-Documented**: 26 architecture decisions guiding development

## 📦 Installation

### Method 1: uvx (Recommended)

```bash
# Run directly without installation
uvx --from gdal-mcp gdal --transport stdio
```

### Method 2: Docker

```bash
# Build and run
docker build -t gdal-mcp .
docker run -i gdal --transport stdio
```

### Method 3: Local Development

```bash
# Clone and install
git clone https://github.com/JordanGunn/gdal-mcp.git
cd gdal-mcp
uv sync
uv run gdal --transport stdio
```

See [QUICKSTART.md](docs/QUICKSTART.md) for detailed setup instructions.
### Method 4: Dev Container (For Contributors)

Use VS Code with the provided devcontainer for a pre-configured development environment:

```bash
# Open in VS Code and select "Reopen in Container"
# Everything is set up automatically!
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [`.devcontainer/README.md`](.devcontainer/README.md) for details.

---

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 🔧 Available Tools

### Raster Tools

#### `raster_info`
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

#### `raster_convert`
Convert raster formats with compression, tiling, and overviews.

**Input**: `uri` (str), `output` (str), optional `options` (ConversionOptions)

**Options**:
- `driver`: Output format (GTiff, COG, PNG, JPEG, etc.)
- `compression`: lzw, deflate, zstd, jpeg, packbits, none
- `tiled`: Create tiled output (default: True)
- `blockxsize`/`blockysize`: Tile dimensions (default: 256×256)
- `overviews`: List of overview levels (e.g., [2, 4, 8, 16])
- `overview_resampling`: nearest, bilinear, cubic, average, mode

**Example**: Convert to Cloud-Optimized GeoTIFF with compression
```python
{
  "uri": "/data/input.tif",
  "output": "/data/output_cog.tif",
  "options": {
    "driver": "COG",
    "compression": "deflate",
    "overviews": [2, 4, 8, 16]
  }
}
```

#### `raster_reproject`
Reproject raster to new CRS with explicit resampling method (ADR-0011 requirement).

**Input**: `uri` (str), `output` (str), `params` (ReprojectionParams)

**Required Params**:
- `dst_crs`: Target CRS (e.g., "EPSG:3857", "EPSG:4326")
- `resampling`: Resampling method (nearest, bilinear, cubic, lanczos, etc.)

**Optional Params**:
- `src_crs`: Override source CRS if missing/incorrect
- `resolution`: Target pixel size as (x, y) tuple
- `width`/`height`: Explicit output dimensions
- `bounds`: Crop to extent (left, bottom, right, top)

**Example**: Reproject DEM to Web Mercator with cubic resampling
```python
{
  "uri": "/data/dem.tif",
  "output": "/data/dem_webmercator.tif",
  "params": {
    "dst_crs": "EPSG:3857",
    "resampling": "cubic"
  }
}
```

#### `raster_stats`
Compute comprehensive statistics for raster bands.

**Input**: `uri` (str), optional `params` (RasterStatsParams)

**Optional Params**:
- `bands`: List of band indices (None = all bands)
- `include_histogram`: Generate histogram (default: False)
- `histogram_bins`: Number of bins (default: 256)
- `percentiles`: Compute specific percentiles (e.g., [25, 50, 75])
- `sample_size`: Sample random pixels for large rasters

**Output**: `RasterStatsResult` with per-band statistics:
- min, max, mean, std, median
- percentile_25, percentile_75
- valid_count, nodata_count
- Optional histogram bins

**Example**: Compute statistics with histogram for band 1
```python
{
  "uri": "/data/landsat.tif",
  "params": {
    "bands": [1],
    "include_histogram": true,
    "percentiles": [10, 25, 50, 75, 90]
  }
}
```

### Vector Tools

#### `vector_info`
Inspect vector dataset metadata using pyogrio (with fiona fallback).

**Input**: `uri` (str)

**Output**: `VectorInfo` with:
- Driver (e.g., "ESRI Shapefile", "GeoJSON", "GPKG")
- CRS, layer count, geometry types
- Feature count, field schema
- Spatial bounds

**Example**: Get metadata for Shapefile
```python
{
  "uri": "/data/parcels.shp"
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

**Current Status**: ✅ 72 tests passing (includes reflection system, prompts, and full integration suite)

Test fixtures create tiny synthetic datasets (10×10 rasters, 3-feature vectors) for fast validation.

## 🔌 Connecting to Claude Desktop

See [QUICKSTART.md](docs/QUICKSTART.md) for full instructions. Quick version:

1. Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "uvx",
      "args": ["--from", "gdal", "gdal", "--transport", "stdio"],
      "env": {
        "GDAL_CACHEMAX": "512"
      }
    }
  }
}
```

2. Restart Claude Desktop
3. Test with: "Use raster_info to inspect /path/to/raster.tif"

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

- [QUICKSTART.md](docs/QUICKSTART.md) - Setup and usage guide
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - Development guide
- [docs/design/](docs/design/) - Architecture and design docs
- [docs/ADR/](docs/ADR/) - Architecture Decision Records

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
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
- ✅ Comprehensive tests (23/23)
- ✅ Docker deployment
- ✅ MCP client integration

**v1.0.0 Achievements** ✅:
- Complete reflection preflight system with epistemic governance
- Domain-aware reasoning prompts (CRS, resampling, hydrology, aggregation)
- Justification schema with persistent context storage
- Full type safety (mypy strict mode) and comprehensive testing
- Agent guidelines for tool awareness and emergent workflows

**Next Phase - Geospatial Analysis**:
- Vector analysis tools (clip, buffer, overlay, query)
- Raster analysis primitives (classify, calc, zonal statistics, contour)
- Semantic reasoning capabilities (urban detection, elevation analysis, water classification)
- Multi-step workflow discovery through tool composition

---

**Status**: v1.0.0 Production Release 🚀

A geospatial reasoning substrate that enables models to compose GDAL operations with domain understanding, justified decisions, and persistent context - unlocking discovery of novel analysis workflows beyond prescribed procedures.

Built with ❤️ for the geospatial AI community.
