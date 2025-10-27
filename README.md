# GDAL MCP

**Geospatial AI with epistemic reasoning**

GDAL MCP is a Model Context Protocol (MCP) server that provides AI agents with geospatial analysis capabilities while requiring them to **justify their methodological choices** through a reflection middleware system.

**🎉 v1.1.1 Released (2025-10-26)** — Vector tool parity + cross-domain reflection validated  
**🧠 Reflection System** — Domain-based epistemic reasoning that transcends data types  
**⚡ 75% Cache Hit Rate** — Methodology reasoning carries across raster ↔ vector operations

[![CI](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/Wayfinder-Foundry/gdal-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP 2.0](https://img.shields.io/badge/FastMCP-2.0-blue.svg)](https://github.com/jlowin/fastmcp)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/gdal-mcp?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/gdal-mcp)

---

## 📚 Documentation

- **[Quick Start](QUICKSTART.md)** - Installation, setup, and MCP configuration
- **[Tools Reference](TOOLS.md)** - Complete tool documentation with examples
- **[Vision](docs/VISION.md)** - Long-term roadmap and philosophy
- **[Changelog](CHANGELOG.md)** - Release history and updates

---

## 🧠 The Reflection System

### What Makes GDAL MCP Different?

Most AI tool systems execute operations immediately when requested. GDAL MCP requires the AI to **justify methodological decisions** before execution, creating a conversation about the "why" rather than just executing the "what."

**Traditional AI tool approach:**
```
User: "Reproject this DEM to Web Mercator"
AI: *silently executes operation*
Result: DEM reprojected (but with what resampling? why that CRS? what tradeoffs?)
```

**GDAL MCP with reflection:**
```
User: "Reproject this DEM to Web Mercator for my web map"
AI: *reflection middleware intercepts*
AI: "Before reprojecting to EPSG:3857, let me justify this CRS choice:
     
     Intent: Web Mercator preserves angles (conformal projection),
             essential for web tile rendering and navigation
     
     Alternatives considered:
     - EPSG:4326 (WGS84) → rejected: not conformal, distorts shapes
     - Local UTM → rejected: limited extent, not web-standard
     
     Tradeoffs: Area distortion increases at high latitudes
                (acceptable for web visualization)
     
     Confidence: High - this is the standard for web mapping"

*justification stored, operation proceeds*
Result: DEM reprojected with documented methodology
```

### Why This Matters

**1. Utilizes Full MCP Protocol Capabilities**

The Model Context Protocol isn't just about tool execution—it's about **agentic reasoning and interaction**. The reflection system leverages MCP's design to enable:
- Pre-execution prompting (tool dependencies)
- Structured reasoning (schema-validated justifications)
- Stateful workflows (justification caching)
- Human-in-the-loop interaction (advisory prompts)

**2. Prevents Silent Failures**

Geospatial operations can execute successfully while producing **methodologically incorrect results**:
- Nearest-neighbor resampling on continuous elevation data (creates artifacts)
- Web Mercator for area calculations (40%+ distortion possible)
- Bilinear interpolation on categorical data (creates invalid class values)

The reflection system **surfaces these choices** for validation.

**3. Educational, Not Restrictive**

The AI isn't blocked from executing operations—it's **required to demonstrate understanding**:
- First use: Explains reasoning, teaches methodology
- Cached: Instant execution (knowledge persists)
- Result: 75%+ cache hit rates, minimal friction

**4. Creates Audit Trail**

Every methodological decision is documented with:
- Intent (what property must be preserved?)
- Alternatives (what else was considered?)
- Rationale (why this choice?)
- Tradeoffs (what are the limitations?)
- Confidence (high/medium/low)

This enables **reproducible geospatial science**.

## 🎯 Example Workflow

### Multi-Operation Geospatial Analysis

```
User: "I need to reproject this DEM to UTM for accurate slope analysis,
       then reproject this vector layer to the same CRS for overlay"

AI Workflow:
1. Inspects DEM metadata (raster_info)
2. REFLECTION: Justifies UTM Zone 10N choice (accurate distance/area)
3. REFLECTION: Justifies cubic resampling (smooth gradients for derivatives)
4. Reprojects DEM (raster_reproject)
5. Inspects vector metadata (vector_info)
6. CACHE HIT: Reuses UTM justification (cross-domain!)
7. Reprojects vector (vector_reproject) - instant, no re-prompting
8. Both datasets now aligned in UTM Zone 10N

Result: 2 operations, 2 reflections (not 3!)
Cache hit rate: 50% → Saves time, maintains methodology
```

**The Key Innovation:** The CRS justification from step 2 is reused in step 6 because the methodology (why UTM Zone 10N?) is **domain-based, not tool-based**. It doesn't matter if you're working with raster or vector data—the projection choice reasoning is the same.

See **[Tools Reference](TOOLS.md)** for detailed examples of all available tools.

## ⚡ Key Features

### 🧠 Reflection Middleware
- Pre-execution reasoning for CRS selection, resampling methods
- Structured justifications (intent, alternatives, choice, tradeoffs, confidence)
- Persistent cache with 75% hit rates in multi-operation workflows
- **Cross-domain cache sharing** - CRS justification works for both raster AND vector

### 🛠️ Comprehensive Toolset
- **Raster tools:** info, convert, reproject, stats
- **Vector tools:** info, reproject, convert, clip, buffer, simplify
- See **[Tools Reference](TOOLS.md)** for complete documentation

### 🛡️ Production Quality
- Full type safety (mypy strict mode)
- 72 passing tests
- Workspace security (path validation middleware)
- Python-native (Rasterio/PyProj/pyogrio)
- Real-time feedback via FastMCP Context API

### 📚 MCP Resources
- Workspace catalog for autonomous file discovery
- Metadata intelligence for format detection  
- Reference knowledge base (CRS, resampling methods, compression options)

## 📦 Quick Start

### Install via uvx (Recommended)

```bash
# Run directly from PyPI
uvx --from gdal-mcp gdal --transport stdio
```

### MCP Configuration (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gdal-mcp": {
      "command": "uvx",
      "args": ["--from", "gdal-mcp", "gdal", "--transport", "stdio"],
      "env": {
        "GDAL_MCP_WORKSPACES": "/path/to/your/geospatial/data"
      }
    }
  }
}
```

**See [QUICKSTART.md](QUICKSTART.md) for:**
- Alternative installation methods (Docker, local development)
- Detailed MCP client configuration
- Workspace security setup
- Troubleshooting guide

## 🔧 Available Tools

GDAL MCP provides 12 production-ready tools across three categories:

### Raster Operations
- `raster_info` - Inspect metadata (CRS, resolution, bands, nodata)
- `raster_convert` - Format conversion with compression & overviews (COG support)
- `raster_reproject` ⚡ - CRS transformation (with reflection)
- `raster_stats` - Statistical analysis with histograms

### Vector Operations
- `vector_info` - Inspect metadata (CRS, geometry, attributes)
- `vector_reproject` ⚡ - CRS transformation (with reflection)
- `vector_convert` - Format migration (SHP ↔ GPKG ↔ GeoJSON)
- `vector_clip` - Spatial subsetting
- `vector_buffer` - Proximity analysis
- `vector_simplify` - Geometry simplification

### Reflection System
- `store_justification` - Cache epistemic reasoning (used internally)
- Advisory prompts for CRS selection and resampling methods

**⚡ = Reflection-enabled:** These tools require methodological justification on first use, then cache for instant subsequent execution.

**See [TOOLS.md](TOOLS.md) for complete documentation with examples and parameters.**

## 🧪 Testing

```bash
# Run all tests
uv run pytest test/ -v

# With coverage
uv run pytest test/ --cov=src --cov-report=term-missing
```

**Status**: ✅ 72 passing tests including reflection system integration

## 🏗️ Architecture

**Python-Native Stack** (ADR-0017):
- **Rasterio** - Raster I/O and manipulation
- **PyProj** - CRS operations and transformations
- **pyogrio** - High-performance vector I/O (fiona fallback)
- **Shapely** - Geometry operations
- **NumPy** - Array operations and statistics
- **Pydantic** - Type-safe models with JSON schema

**Key Design Decisions** ([26 ADRs](docs/ADR/) guide development):
- ADR-0026: Reflection system and epistemic governance
- ADR-0017: Python-native over CLI shelling for performance
- ADR-0011: Explicit resampling required (prevents silent data corruption)
- ADR-0022: Workspace isolation for security

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

**Current Status: v1.1.1** - Phase 2 Complete ✅
- Reflection middleware operational
- Vector/raster tool parity achieved  
- Cross-domain cache sharing validated (75% hit rates)

**Next: Phase 3 - Workflow Intelligence (v2.0+)**
- Formal workflow composition
- Multi-step orchestration
- Analysis pattern libraries

See **[Vision](docs/VISION.md)** for the complete long-term roadmap.

---

**Built with ❤️ for the geospatial AI community**

*Geospatial operations that think, not just execute.*
