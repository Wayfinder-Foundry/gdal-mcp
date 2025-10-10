---
status: accepted
date: 2025-10-09
decision-makers: [jgodau, cascade-ai]
tags: [architecture, mcp, resources, taxonomy, agentic-reasoning]
---

# ADR-0023: Resource Taxonomy and Hierarchy

## Context

GDAL MCP aims to enable agentic geospatial reasoning where AI agents can discover data, understand context, and make informed decisions autonomously. The MCP protocol provides three primitives: Tools (execute operations), Resources (read information), and Prompts (guide thinking).

Initial implementation focused on Tools, but agentic reasoning requires AI to access contextual information before and during execution. Without structured Resources, AI operates blindly, requiring constant user input for basic information like "what files exist?" or "what CRS should I use?"

Furthermore, some existing Tools (e.g., `raster_info`, `vector_info`) are actually read-only operations that should be Resources, not Tools, according to MCP semantics.

## Decision

We adopt a **four-category resource taxonomy** with hierarchical URI organization:

### Category 1: Metadata Resources
**Purpose**: Information ABOUT specific geospatial data  
**Pattern**: `metadata://{identifier}/{aspect}`  
**Characteristics**: Dynamic, file-specific, computed on-demand

**Resources**:
- `metadata://{file}/raster` - Raster spatial properties (CRS, bounds, resolution, bands, dtype, nodata)
- `metadata://{file}/vector` - Vector spatial properties (CRS, bounds, geometry type, feature count, fields)
- `metadata://{file}/format` - File format and driver information
- `metadata://{file}/statistics` - Computed statistics (min/max/mean/std, histogram)

**Scope**: 4-6 resources

### Category 2: Catalog Resources
**Purpose**: Discover what data EXISTS in the workspace  
**Pattern**: `catalog://{scope}/{filter}`  
**Characteristics**: Dynamic, workspace-specific, updated on query

**Resources**:
- `catalog://workspace/all` - All geospatial files in allowed workspaces
- `catalog://workspace/raster` - All raster files
- `catalog://workspace/vector` - All vector files
- `catalog://workspace/by-crs/{epsg}` - Files in specific CRS
- `catalog://workspace/summary` - Workspace statistics

**Scope**: 5-7 resources

### Category 3: Reference Resources
**Purpose**: Static domain knowledge and system capabilities  
**Pattern**: `reference://{domain}/{topic}`  
**Characteristics**: Static or rarely-changing, educational, enumeration of capabilities

**Resources**:
- `reference://crs/common` - Common CRS by use case and region
- `reference://crs/{epsg}` - Detailed CRS information (via pyproj)
- `reference://drivers/raster` - Available raster drivers (from rasterio)
- `reference://drivers/vector` - Available vector drivers (from pyogrio/fiona)
- `reference://resampling/available` - Available resampling methods (from rasterio.enums.Resampling)
- `reference://resampling/guide` - When to use each resampling method (curated)
- `reference://compression/available` - Available compression methods (from GDAL/rasterio)
- `reference://compression/guide` - Compression trade-offs and recommendations
- `reference://formats/raster` - Raster format reference
- `reference://formats/vector` - Vector format reference
- `reference://terrain/parameters` - Terrain analysis parameters
- `reference://terrain/algorithms` - Available terrain algorithms
- `reference://glossary/geospatial` - Domain terminology reference

**Scope**: 13-15 resources

### Category 4: Context Resources
**Purpose**: Session state and processing history  
**Pattern**: `context://{aspect}` or `history://{scope}`  
**Characteristics**: Session-specific, temporal, enables continuity

**Resources**:
- `context://session/current` - Current session information
- `context://workspace/config` - Workspace configuration
- `context://analysis/current` - Current analysis context
- `history://operations/recent` - Recent processing operations
- `history://operations/by-file/{file}` - File provenance
- `history://session/timeline` - Session timeline

**Scope**: 6-8 resources

**Total**: 28-36 resources across 4 categories

## Rationale

### Why Four Categories?

1. **Metadata** - AI needs to understand file properties before operating
2. **Catalog** - AI needs to discover what data exists without asking user
3. **Reference** - AI needs domain knowledge to make informed decisions
4. **Context** - AI needs session continuity for multi-step workflows

### Why Hierarchical URIs?

- **Discoverability**: Clear organization enables AI to find relevant resources
- **Extensibility**: Easy to add new resources within existing categories
- **Semantics**: URI pattern indicates resource purpose and characteristics
- **Consistency**: Predictable naming reduces AI confusion

### Why Separate Enumeration from Guidance?

Resources like `reference://resampling/available` (system capabilities from rasterio) are distinct from `reference://resampling/guide` (curated expertise on when to use each). This separation enables:
- **Discovery**: "What methods exist?"
- **Decision-making**: "Which method should I use?"

### Migration of Existing Tools

`raster_info` and `vector_info` are read-only operations (no side effects) and should be Resources according to MCP semantics. However, users may explicitly request formatted metadata display.

**Solution**: Dual implementation
- **Resource**: `metadata://{file}/raster` - AI queries during planning
- **Tool**: `raster_info` - User explicitly requests formatted output
- Both share underlying implementation

## Consequences

### Positive

- **Autonomous AI**: Can discover data and make informed decisions without user input
- **Agentic Workflows**: Resources enable ReAct-style reasoning (plan → act → observe)
- **Reduced User Friction**: AI asks fewer questions, operates more independently
- **Knowledge Infrastructure**: Reference resources encode domain expertise
- **Session Continuity**: Context resources enable multi-turn conversations
- **Proper MCP Semantics**: Read-only operations correctly implemented as Resources

### Negative

- **Implementation Effort**: 28-36 resources to implement (phased over 8 weeks)
- **Maintenance**: Reference resources require updates as capabilities evolve
- **Caching Complexity**: Some resources (catalog, metadata) need intelligent caching
- **Migration Required**: Existing `raster_info`/`vector_info` tools need dual implementation

### Neutral

- **API Surface Growth**: More discoverable endpoints, but organized hierarchically
- **Documentation Burden**: Each resource needs clear documentation for AI understanding

## Implementation Plan

### Phase 2A: Foundation (Week 1-2) - 10 CRITICAL resources
**Priority 1**: Workspace Discovery (3)
- `catalog://workspace/all`
- `catalog://workspace/raster`
- `catalog://workspace/vector`

**Priority 2**: File Metadata (2)
- `metadata://{file}/raster`
- `metadata://{file}/vector`

**Priority 3**: Essential References (5)
- `reference://crs/common`
- `reference://resampling/available`
- `reference://resampling/guide`
- `reference://compression/available`
- `reference://glossary/geospatial`

**Deliverable**: AI can discover data, understand properties, make informed decisions

### Phase 2B: Enhanced Discovery (Week 3-4) - 6 resources
Catalog expansion, metadata expansion, reference expansion

### Phase 2C: Context & History (Week 5-6) - 6 resources
Context resources, history resources for provenance

### Phase 2D: Domain-Specific References (Week 7-8) - 6 resources
Terrain analysis, format references, advanced guides

## Module Organization

```
src/resources/
├── __init__.py          # Shared utilities, workspace discovery
├── metadata.py          # Metadata resources (4-6)
├── catalog.py           # Catalog resources (5-7)
├── reference.py         # Reference resources (13-15)
└── context.py           # Context/history resources (6-8)
```

## Example Usage

**Autonomous workflow enabled by resources:**

```
User: "Reproject all DEMs to Web Mercator"

AI Reasoning:
1. Read catalog://workspace/raster → find all rasters
2. For each raster:
   - Read metadata://{file}/raster → check if DEM (single band, elevation)
   - Read reference://crs/common → confirm Web Mercator is EPSG:3857
   - Read reference://resampling/guide → choose cubic for elevation
   - Execute raster_reproject with appropriate parameters
3. Report: "Reprojected 3 DEMs to EPSG:3857 using cubic resampling"
```

**No user questions needed. Complete autonomous workflow.**

## Related Decisions

- **ADR-0022**: Workspace Scoping - Catalog resources respect workspace boundaries
- **ADR-0020**: Context-Driven Tool Design - Resources provide context for tool usage
- **ADR-0021**: LLM-Optimized Tool Descriptions - Resources complement tool descriptions
- **Three-Pillar Architecture Decision** (ConPort): Resources/Tools/Prompts separation

## References

- [MCP Specification - Resources](https://spec.modelcontextprotocol.io/specification/server/resources/)
- [FastMCP Resources Guide](https://github.com/jlowin/fastmcp/blob/main/docs/servers/resources.mdx)
- `docs/fastmcp/DECORATORS.md` - Decision guide for choosing decorators
- `docs/fastmcp/RESOURCES.md` - Resource implementation guide (in progress)
- `projectBrief.md` - Vision for agentic geospatial reasoning

## Status

**Accepted** - 2025-10-09

Implementation begins with Phase 2A (10 critical resources) in Week 1-2 of Phase 2 development.
