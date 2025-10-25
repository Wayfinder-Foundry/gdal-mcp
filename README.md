# GDAL MCP

**The first geospatial AI substrate with epistemic reasoning**

> *"Before reprojecting to EPSG:3857, why is this CRS appropriate for your analysis? What spatial properties must be preserved? What distortion tradeoffs are acceptable?"*

GDAL MCP doesn't just execute geospatial operations—it **thinks through them**. Built on FastMCP with a reflection middleware that requires AI agents to justify methodological decisions before execution.

**🎉 v1.0.0 Released (2025-10-24)** — First MCP server with built-in epistemic governance  
**🧠 Reflection System** — Pre-execution reasoning for CRS, resampling, hydrology, and aggregation

[![CI](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.0](https://img.shields.io/badge/FastMCP-2.0-blue.svg)](https://github.com/jlowin/fastmcp)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/gdal-mcp?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/gdal-mcp)

## 🧠 Why Reflection Matters

**Geospatial operations have consequences.** Choosing the wrong resampling method can introduce false elevation data. Selecting an inappropriate CRS can distort area calculations by 40%. Aggregating without understanding data distribution can hide critical outliers.

**Traditional approach:**
```
User: "Reproject this DEM to Web Mercator"
AI: *immediately executes gdal.Warp()*
```

**GDAL MCP with reflection:**
```
User: "Reproject this DEM to Web Mercator for a web map"
AI: *triggered to justify CRS choice*
    "Before reprojecting to EPSG:3857:
     - Intent: Preserve angular relationships for web tile rendering
     - Alternatives considered: EPSG:4326 (rejected: not conformal)
     - Tradeoffs: Distance/area distortion at high latitudes acceptable for visualization
     - Confidence: High"
*stores justification, proceeds with operation*
```

The AI doesn't just follow instructions—it **understands the methodology**.

## 🎯 Real-World Examples

### Example 1: DEM Reprojection with Methodological Reasoning

**Scenario:** You need to reproject a 30m elevation model from WGS84 to UTM for slope analysis.

**User prompt:**
```
Reproject my DEM from test/data/elevation.tif to UTM Zone 10N. 
I need accurate slope calculations.
```

**What happens:**

1. **AI inspects the source:** `raster_info` reveals EPSG:4326, 30m resolution
2. **Reflection triggered (CRS):**
   - Why UTM Zone 10N (EPSG:32610)?
   - Intent: Preserve distance accuracy for slope/aspect calculations
   - Alternative: Web Mercator (EPSG:3857) — rejected, non-conformal distortion
   - Tradeoff: Limited to ~6° longitude zone, acceptable for local analysis
3. **Reflection triggered (Resampling):**
   - Why cubic convolution?
   - Intent: Smooth gradients while preserving elevation values
   - Alternative: Nearest neighbor — rejected, creates blocky artifacts in slope
   - Alternative: Bilinear — rejected, cubic provides superior smoothness for derivatives
4. **Execution:** Reprojection proceeds with cached justifications
5. **Result:** Properly reprojected DEM with documented methodology

**Cache behavior:** Next time you reproject *any* DEM to UTM with cubic, no re-justification needed.

### Example 2: Multi-Resolution COG Creation

**User prompt:**
```
Create a Cloud-Optimized GeoTIFF from this 10GB Landsat scene.
Optimize for web serving with multiple zoom levels.
```

**What happens:**

1. **AI plans the operation:** Convert with compression + overviews
2. **Smart defaults applied:**
   - Driver: COG (Cloud-Optimized GeoTIFF)
   - Compression: DEFLATE (lossless, good ratio)
   - Tiling: 256×256 blocks (web-optimized)
   - Overviews: [2, 4, 8, 16] (zoom levels)
3. **Execution with real-time feedback:**
   ```
   Building overviews [2, 4, 8, 16]...
   Output: 1.2GB (88% reduction)
   Validation: ✓ COG structure valid
   ```

### Example 3: Cache Intelligence

**First request:**
```
Reproject this imagery to EPSG:3857 using cubic resampling for a web map.
```
→ Triggers both CRS and resampling justifications (~30 seconds)

**Second request (same session):**
```
Now reproject this other tile to EPSG:3857 with cubic for the same map.
```
→ Cache hit! Both justifications reused (instant)

**Third request (different parameter):**
```
Actually, use bilinear instead to reduce processing time.
```
→ CRS justification cached, only resampling re-justified

## ⚡ Key Features

### 🧠 Reflection System (v1.0.0)

**The core innovation:** FastMCP middleware that intercepts tool calls and enforces epistemic discipline.

- **Pre-execution reasoning prompts** for operations with methodological implications
- **Structured justifications** (intent → alternatives → choice → tradeoffs → confidence)
- **Persistent cache** (`.preflight/justifications/{domain}/`) with SHA256-based lookup
- **Domain-specific reasoning:** CRS/datum, resampling, hydrology conditioning, aggregation
- **Automatic cache hits:** Same parameters = instant execution (no re-justification)

**Reflection domains:**
- `crs_datum` — Coordinate system selection and datum transformations
- `resampling` — Interpolation method choice for raster operations  
- `hydrology` — Flow direction, watershed delineation, DEM conditioning *(planned)*
- `aggregation` — Zonal statistics, temporal composites, data fusion *(planned)*

**How it works:**
1. User requests operation with methodological choices (e.g., "reproject to UTM")
2. Middleware intercepts `raster_reproject` call, checks cache
3. If no justification exists → triggers `justify_crs_selection` prompt
4. AI provides structured reasoning → stored with hash key
5. Operation proceeds with validated methodology
6. Future requests with same parameters skip justification (cache hit)

**See:** [test/REFLECTION_TESTING.md](test/REFLECTION_TESTING.md) for comprehensive testing guide with 7 scenarios

### 🛡️ Production Quality

- **Type-safe:** Full mypy strict mode, Pydantic models with JSON schemas
- **Tested:** 72 passing tests including reflection system integration
- **Secure:** PathValidationMiddleware for workspace isolation (no directory traversal)
- **Fast:** Python-native (Rasterio/GDAL bindings, no CLI shelling)
- **Observable:** Real-time feedback during long operations via FastMCP Context API

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
Inspect raster metadata without reading pixel data.

**Use cases:** Understand projection, resolution, extent before processing

**Input:** `uri` (path to raster)

**Output:** Driver, CRS, bounds, transform, dimensions, data type, nodata value, overview levels

**Example conversation:**
```
User: "What's the CRS and resolution of elevation.tif?"
AI: *calls raster_info*
    "The DEM is in EPSG:4326 (WGS84) with 0.000277° resolution (~30m at equator).
     It covers bounds: [-122.5, 37.5, -122.0, 38.0]"
```

#### `raster_convert`
Format conversion with compression and multi-resolution overviews.

**Use cases:** Create Cloud-Optimized GeoTIFFs, reduce file size, build pyramids for fast rendering

**Key options:**
- `driver`: GTiff, COG, PNG, JPEG (COG = Cloud-Optimized GeoTIFF)
- `compression`: deflate, lzw, zstd, jpeg (case-insensitive)
- `tiled`: 256×256 blocks for efficient partial reads
- `overviews`: [2, 4, 8, 16] for multi-resolution display

**Example conversation:**
```
User: "Optimize this 5GB satellite image for web serving"
AI: "Converting to COG with DEFLATE compression and overviews..."
    *calls raster_convert with driver=COG, compression=deflate, overviews=[2,4,8,16]*
    "Done! Reduced to 1.2GB (76% savings). Ready for cloud storage with efficient range requests."
```

#### `raster_reproject` ⚡ *Reflection-enabled*
Reproject to new coordinate system with methodological justification.

**🧠 Triggers reflection for:**
- **CRS selection** — Why this projection? What properties must be preserved?
- **Resampling method** — How to interpolate? What artifacts are acceptable?

**Use cases:** Transform to analysis-appropriate CRS, align multiple datasets, prepare for web mapping

**Required parameters:**
- `dst_crs`: Target projection (e.g., "EPSG:32610" for UTM Zone 10N)
- `resampling`: Interpolation method
  - `nearest` — Categorical data (land cover, classified imagery)
  - `bilinear` — Fast, good for continuous data
  - `cubic` — Smoothest, best for DEMs and visualization
  - `lanczos` — Highest quality, slower

**Optional parameters:**
- `resolution`: Target pixel size [x, y] in destination units
- `bounds`: Crop to area of interest [left, bottom, right, top]

**Example conversation:**
```
User: "Reproject this land cover map to UTM for area calculations"
AI: *raster_info shows categorical data*
    *reflection: Why UTM? → accurate area/distance in local zone*
    *reflection: Why nearest? → preserves exact class values, no new categories*
    "Reprojecting to EPSG:32610 with nearest-neighbor to preserve classification..."
    *executes with justified methodology*
```

#### `raster_stats`
Compute statistical summaries and histograms.

**Use cases:** Understand data distribution, find outliers, validate processing results

**Output:** min, max, mean, std, median, percentiles, histogram (optional)

**Example conversation:**
```
User: "Check the elevation range in this DEM"
AI: *calls raster_stats*
    "Elevation ranges from 145m to 2,847m with mean 892m.
     Distribution shows two peaks (bimodal) - likely valley and ridge areas."
```

### Vector Tools

#### `vector_info`
Inspect vector dataset metadata (Shapefile, GeoJSON, GeoPackage, etc.).

**Output:** Driver, CRS, geometry types, feature count, field schema, bounds

**Example conversation:**
```
User: "What's in this shapefile?"
AI: *calls vector_info*
    "It's a polygon layer with 1,247 parcels in EPSG:2227 (California State Plane).
     Fields: parcel_id (string), area_sqft (float), zoning (string), assessed_value (int)"
```

### Reflection Tools

#### `store_justification`
Explicitly cache epistemic justifications (used internally by reflection system).

**Purpose:** Allows AI to store methodological reasoning for future operations

**When called:** Automatically after reflection prompts, or manually for custom workflows

**Cache structure:** `.preflight/justifications/{domain}/sha256:{hash}.json`

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

**Getting Started:**
- [QUICKSTART.md](docs/QUICKSTART.md) — Installation and Claude Desktop setup
- [REFLECTION_TESTING.md](test/REFLECTION_TESTING.md) — Testing the reflection system

**Development:**
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) — Development guide and standards
- [docs/design/](docs/design/) — Architecture and design documentation
- [docs/ADR/](docs/ADR/) — 26 Architecture Decision Records

**Key ADRs:**
- [ADR-0026](docs/ADR/0026-prompting-and-epistemic-governance.md) — Reflection system design
- [ADR-0011](docs/ADR/0011-explicit-resampling-required.md) — Why resampling must be explicit
- [ADR-0017](docs/ADR/0017-python-native-over-cli.md) — Python bindings over CLI shelling
- [ADR-0022](docs/ADR/0022-path-validation-middleware.md) — Workspace isolation security

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

## 🗺️ Roadmap

### ✅ v1.0.0 — Epistemic Foundation (Released 2025-10-24)

**Reflection middleware:**
- Pre-execution reasoning for CRS selection and resampling methods
- Persistent justification cache with SHA256-based lookup
- Structured justifications (intent, alternatives, choice, tradeoffs, confidence)
- Integration with `raster_reproject` tool

**Production infrastructure:**
- Full type safety (mypy strict mode)
- 72 passing tests with reflection system coverage
- PathValidationMiddleware for workspace security
- FastMCP 2.0 with native middleware support

### 🚧 v1.1.0 — Extended Reflection Domains (Q1 2025)

**New reflection triggers:**
- Hydrology conditioning (DEM preprocessing, flow accumulation parameters)
- Aggregation strategies (zonal statistics, temporal composites, resampling for aggregation)
- Format selection (when to use COG vs JPEG vs PNG, compression tradeoffs)

**Workflow composition:**
- Multi-step analysis discovery ("analyze watershed from this DEM")
- Chain justifications (reproject → condition → flow direction → watershed)
- Provenance tracking across operations

### 🔮 v2.0.0 — Analysis Primitives (Q2 2025)

**Vector analysis:**
- Spatial joins and overlays with geometric reasoning
- Buffer/clip operations with distance unit justification
- Attribute queries with SQL generation

**Raster analysis:**
- Classification with threshold justification
- Raster calculator with band math validation
- Zonal statistics with aggregation reflection
- Contour generation with interval selection

**Semantic capabilities:**
- Urban area detection from imagery
- Terrain analysis workflows (slope → aspect → hillshade)
- Water body classification with spectral reasoning

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed milestones and technical planning.

---

## 🎓 Learn More

- **[Quick Start Guide](docs/QUICKSTART.md)** — Setup and first operations
- **[Reflection Testing Guide](test/REFLECTION_TESTING.md)** — 7 scenarios testing cache behavior
- **[Architecture Decisions](docs/ADR/)** — 26 ADRs documenting design choices
- **[Contributing Guide](docs/CONTRIBUTING.md)** — Development setup and standards

---

**Status:** v1.0.0 Production Release 🚀

*The first geospatial MCP server that doesn't just execute operations—it reasons about them.*

**Core innovation:** Epistemic governance through reflection middleware. AI agents must justify methodological choices (CRS, resampling, aggregation) before execution. Justifications are cached for workflow efficiency while maintaining scientific rigor.

**Vision:** Enable discovery of novel geospatial analysis workflows through tool composition with domain understanding, not just prescribed procedures.

Built with ❤️ for the geospatial AI community.
