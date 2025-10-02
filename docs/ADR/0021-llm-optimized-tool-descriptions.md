# ADR-0021: LLM-Optimized Tool Descriptions and Metadata

**Status**: Accepted  
**Date**: 2025-09-30 
**Deciders**: Jordan Godau 
**Tags**: #mcp #llm #discoverability #tool-design

## Context

MCP tools are **discovered and invoked by LLMs**, not humans. Traditional API documentation patterns (concise descriptions, external docs) don't work because:

1. **LLMs choose tools** based solely on name + description + input schema
2. **No external documentation** - LLM can't browse docs or examples
3. **Decision guidance needed** - LLM must decide WHEN to use a tool
4. **Output format matters** - LLM needs to know what it will receive

**Current state**: Our tool descriptions are **human-focused**:
```python
@mcp.tool(description="Convert raster format with options")
```

**Problem**: LLM doesn't know:
- When to use this vs. other tools
- What "options" are available
- What output format to expect
- Whether this has side effects

**MCP/FastMCP best practices**:
- Rich, detailed descriptions with decision guidance
- Use `readOnlyHint` / `destructiveHint` for safety signaling
- Include use cases, output format, and side effects
- Add tags for categorization

## Decision

**Adopt LLM-optimized tool descriptions** with structured format:

### Description Template

```
[Brief one-liner]. [Extended explanation].

USE WHEN: [Decision guidance - when to choose this tool]
REQUIRES: [Mandatory parameters with examples]
OPTIONAL: [Optional parameters]
OUTPUT: [What LLM will receive]
SIDE EFFECTS: [File creation, modification, etc.]
```

### Metadata Requirements

1. **Safety hints** - Every tool must declare:
   - `readOnlyHint=True` for read-only operations
   - `destructiveHint=True` for file-modifying operations

2. **Tags** - Categorize for filtering:
   - `["raster", "metadata"]` for info tools
   - `["raster", "processing"]` for conversion tools
   - `["vector", "metadata"]` for vector.info

3. **Clear examples** in descriptions

## Rationale

### Why LLM-Optimized Descriptions?

**Traditional API description**:
```python
description="Reproject a raster to a new CRS"
```

**LLM sees**: Generic statement, no decision guidance
**Result**: LLM might use wrong tool or ask user for clarification

**LLM-optimized description**:
```python
description=(
    "Reproject raster to new coordinate reference system with explicit resampling. "
    "USE WHEN: Coordinate system doesn't match target OR "
    "need different projection for analysis. "
    "REQUIRES: dst_crs (e.g. 'EPSG:3857' for Web Mercator) and resampling method "
    "(nearest, bilinear, cubic, lanczos - see ADR-0011). "
    "OUTPUT: ReprojectionResult with ResourceRef to output file, transform, and bounds. "
    "SIDE EFFECTS: Creates new file at output path."
)
```

**LLM sees**: Clear decision tree, required params with examples, output format
**Result**: LLM makes informed decision and constructs correct call

### Why Safety Hints?

**Without hints**:
```python
@mcp.tool(name="raster.convert")
```

**LLM assumption**: Unknown whether this is safe or destructive

**With hints**:
```python
@mcp.tool(
    name="raster.convert",
    readOnlyHint=False,
    destructiveHint=True,  # Creates new file
)
```

**Benefit**: MCP clients can:
- Show warning icons for destructive operations
- Require additional confirmation
- Log safety-critical operations

### Why Tags?

Enable filtering and organization:
```python
# LLM can filter: "Show me all raster processing tools"
tools = [t for t in available_tools if "processing" in t.tags]

# Or: "Show me read-only tools"
safe_tools = [t for t in available_tools if t.readOnlyHint]
```

## Implementation Guidelines

### Pattern for Read-Only Tools

```python
@mcp.tool(
    name="raster.info",
    description=(
        "Inspect raster metadata using Python-native Rasterio. "
        "USE WHEN: Need to understand raster properties before processing, "
        "verify CRS and bounds, check band count and data types, or inspect nodata values. "
        "REQUIRES: uri (path or URI to raster file). "
        "OPTIONAL: band (1-based band index for overview introspection). "
        "OUTPUT: RasterInfo with driver, CRS, width, height, count, dtype, "
        "transform (6-element affine), bounds (minx, miny, maxx, maxy), "
        "nodata value, overview levels, and tags dict. "
        "SIDE EFFECTS: None (read-only operation)."
    ),
    readOnlyHint=True,
)
async def raster_info(uri: str, band: int | None = None, ctx: Context | None = None):
    ...
```

### Pattern for Processing Tools

```python
@mcp.tool(
    name="raster.convert",
    description=(
        "Convert raster format with compression, tiling, and overview generation. "
        "USE WHEN: Need to change format (e.g. GeoTIFF to COG), apply compression "
        "to reduce file size, create tiled output for performance, or build overviews "
        "for faster display at multiple scales. "
        "REQUIRES: uri (source raster), output (destination path). "
        "OPTIONAL: options (ConversionOptions) with driver (GTiff, COG, PNG, JPEG), "
        "compression (lzw, deflate, zstd, jpeg, packbits), tiling (blockxsize/blockysize), "
        "overviews (list of levels like [2, 4, 8]), overview_resampling (nearest, average). "
        "OUTPUT: ConversionResult with ResourceRef (output file URI and size), "
        "driver name, compression used, and overviews_built list. "
        "SIDE EFFECTS: Creates new file at output path."
    ),
    readOnlyHint=False,
    destructiveHint=True,
)
async def raster_convert(
    uri: str,
    output: str,
    options: ConversionOptions | None = None,
    ctx: Context | None = None,
):
    ...
```

### Pattern for Complex Tools

```python
@mcp.tool(
    name="raster.reproject",
    description=(
        "Reproject raster to new CRS with explicit resampling method (ADR-0011 requirement). "
        "USE WHEN: Coordinate system doesn't match target projection OR "
        "data needs different spatial reference for analysis/overlay. "
        "REQUIRES: uri (source raster), output (destination path), "
        "params (ReprojectionParams) with dst_crs (e.g. 'EPSG:3857', 'EPSG:4326') "
        "and resampling method (nearest for categorical, bilinear/cubic for continuous). "
        "OPTIONAL: src_crs (override source), resolution (target pixel size as (x, y)), "
        "width/height (output dimensions), bounds (crop extent), nodata (output nodata value). "
        "OUTPUT: ReprojectionResult with ResourceRef to output file, src_crs used, "
        "dst_crs, resampling method, output transform (6-element affine), "
        "width, height, and bounds in destination CRS. "
        "SIDE EFFECTS: Creates new file at output path. "
        "NOTE: Resampling method is REQUIRED per ADR-0011 (no defaults to prevent data corruption)."
    ),
    readOnlyHint=False,
    destructiveHint=True,
)
async def raster_reproject(
    uri: str,
    output: str,
    params: ReprojectionParams,
    ctx: Context | None = None,
):
    ...
```

## Description Structure Breakdown

**Format**:
```
[One-line summary]. [Extended explanation].

USE WHEN: [Decision tree - helps LLM choose]
REQUIRES: [Mandatory params with concrete examples]
OPTIONAL: [Optional params with defaults/examples]
OUTPUT: [Exact structure LLM will receive]
SIDE EFFECTS: [File creation, API calls, etc.]
NOTE: [Critical considerations, ADR references]
```

**Why this structure**:

| Section | Purpose | Example |
|---------|---------|---------|
| **One-liner** | Quick scan | "Reproject raster to new CRS" |
| **Extended** | Context | "...with explicit resampling method" |
| **USE WHEN** | Decision guidance | "Coordinate system doesn't match..." |
| **REQUIRES** | Mandatory params | "dst_crs (e.g. 'EPSG:3857')" |
| **OPTIONAL** | Optional params | "resolution (target pixel size)" |
| **OUTPUT** | Return structure | "ReprojectionResult with ResourceRef..." |
| **SIDE EFFECTS** | Safety info | "Creates new file at output path" |
| **NOTE** | Critical info | "Resampling REQUIRED per ADR-0011" |

## Consequences

**Positive**:
- ✅ **Better tool selection** - LLM chooses correct tool
- ✅ **Fewer errors** - LLM constructs valid calls
- ✅ **Self-documenting** - No external docs needed
- ✅ **Safety awareness** - Hints signal destructive operations
- ✅ **Discoverability** - Tags enable filtering

**Negative**:
- ⚠️ **Verbose descriptions** - Can be 5-10x longer
- ⚠️ **Maintenance overhead** - Must update descriptions with code changes
- ⚠️ **Token usage** - Longer descriptions use more tokens

**Neutral**:
- Descriptions live with code (easy to keep in sync)
- One-time cost to write, ongoing benefit

## Comparison: Before vs After

### Before (Human-focused)
```python
@mcp.tool(
    name="raster.stats",
    description="Compute comprehensive statistics for raster bands"
)
async def raster_stats(uri: str, params: RasterStatsParams | None = None):
    ...
```

**LLM understanding**: 🤷 "What kind of statistics? When do I use this?"

### After (LLM-optimized)
```python
@mcp.tool(
    name="raster.stats",
    description=(
        "Compute comprehensive statistics for raster bands including "
        "min/max/mean/std/median/percentiles and optional histogram. "
        "USE WHEN: Need to analyze data distribution, find outliers, "
        "understand value ranges, or generate histograms for visualization. "
        "REQUIRES: uri (path to raster). "
        "OPTIONAL: params (RasterStatsParams) with bands (list of indices, "
        "None=all), include_histogram (bool), histogram_bins (2-1024, default 256), "
        "percentiles (list like [25, 50, 75]), sample_size (for large rasters). "
        "OUTPUT: RasterStatsResult with per-band BandStatistics (min, max, mean, "
        "std, median, percentile_25, percentile_75, valid_count, nodata_count) "
        "and optional histogram (list of HistogramBin with min/max/count). "
        "SIDE EFFECTS: None (read-only, computes in-memory)."
    ),
    readOnlyHint=True,
)
async def raster_stats(
    uri: str,
    params: RasterStatsParams | None = None,
    ctx: Context | None = None,
):
    ...
```

**LLM understanding**: 🎯 "Use for data distribution analysis. Returns structured stats per band. Read-only."

## Related

- **ADR-0020**: Context-Driven Tool Design - Complements with runtime feedback
- **ADR-0011**: Explicit Resampling - Referenced in descriptions
- **FastMCP Guidelines**: Tool metadata and description best practices

## References

- [FastMCP Tool Metadata](https://gofastmcp.com)
- [MCP Specification - Tool Discovery](https://modelcontextprotocol.io)
- LLM prompt engineering: Clear, structured, example-rich descriptions
