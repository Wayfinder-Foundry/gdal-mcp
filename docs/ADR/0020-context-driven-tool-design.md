# ADR-0020: Context-Driven Tool Design for MCP

**Status**: Accepted  
**Date**: 2025-09-30  
**Deciders**: Jordan Gunn, Cascade AI  
**Tags**: #mcp #fastmcp #context #ux #logging

## Context

MCP servers differ fundamentally from traditional REST APIs in their communication patterns:

1. **Audience**: Tools are consumed by LLMs, not humans directly
2. **Feedback loop**: LLMs need real-time progress/logging to understand execution
3. **Long operations**: Geospatial processing can take seconds to minutes
4. **Error context**: LLMs need actionable error messages to provide user guidance

**Current state** (MVP): Tools run silently with no intermediate feedback. On long operations:
- Users see a spinner with no progress indication
- LLMs have no visibility into what's happening
- Errors return Python tracebacks instead of actionable messages

**MCP/FastMCP best practices** emphasize:
- Use `Context` parameter for logging, progress, and resource access
- Send diagnostic messages to LLM via `ctx.info()`, `ctx.debug()`, `ctx.error()`
- Report progress for operations >1 second via `ctx.report_progress()`
- Use `ToolError` for user-friendly error messages

## Decision

**Adopt Context-driven tool design** for all GDAL MCP tools:

1. **Add Context parameter** to all tool signatures:
   ```python
   from mcp.server import Context
   
   async def tool_function(
       uri: str,
       params: SomeParams,
       ctx: Context | None = None,  # Optional for backward compatibility
   ) -> Result:
   ```

2. **Log key execution steps** to provide LLM visibility:
   ```python
   if ctx:
       await ctx.info("Opening raster...")
       await ctx.debug(f"Source CRS: {src.crs}")
   ```

3. **Report progress** for operations >1 second:
   ```python
   if ctx:
       await ctx.report_progress(current, total)
   ```

4. **Use ToolError** for actionable errors:
   ```python
   from mcp.types import ToolError
   
   raise ToolError(
       f"Cannot open '{uri}'. Ensure file exists and is valid. "
       f"Supported formats: GeoTIFF, COG, PNG."
   )
   ```

5. **Context is optional** - tools work without it but provide degraded UX

## Rationale

### Why Context?

**Problem**: Silent execution on 5GB raster reprojection
- **Without Context**: User sees spinner for 60s, no feedback, assumes it's hung
- **With Context**: "Opening raster... Source: 5000x5000... Processing band 1/3... 33% complete... 67%... Done!"

**Benefits**:

| Stakeholder | Without Context | With Context |
|-------------|----------------|--------------|
| **User** | "Is it working?" | Real-time progress |
| **LLM** | No visibility | Step-by-step understanding |
| **Developer** | Hard to debug | Structured logging |

### Why Optional Context?

Makes tools usable in non-MCP contexts (tests, direct API calls):
```python
# MCP call - full UX
result = await tool(uri, params, ctx=mcp_context)

# Test call - no Context needed
result = await tool(uri, params)  # Works fine
```

### Logging Strategy

**Traditional API logging** (for ops teams):
```python
logger.info("Processing request")  # Goes to files/stderr
```

**MCP logging** (for LLM/users):
```python
await ctx.info("Processing request")  # Goes to LLM/client
```

**Both are needed** but serve different purposes.

### Message Level Guidelines

| Level | Purpose | Example |
|-------|---------|---------|
| `ctx.debug()` | Detailed diagnostics | "Source CRS: EPSG:4326" |
| `ctx.info()` | Key milestones | "Opening raster... Processing... Done!" |
| `ctx.error()` | Failures | "Failed to open file" |
| `ctx.report_progress()` | Long operations | 33%, 67%, 100% |

## Implementation Pattern

### Read-Only Tools (info, stats)

```python
async def get_raster_info(uri: str, ctx: Context | None = None) -> RasterInfo:
    """Inspect raster metadata with progress logging."""
    
    if ctx:
        await ctx.info(f"📂 Opening raster: {uri}")
    
    try:
        with rasterio.open(uri) as ds:
            if ctx:
                await ctx.debug(f"Driver: {ds.driver}, CRS: {ds.crs}")
            
            # Build result...
            
            if ctx:
                await ctx.info("✓ Metadata extracted successfully")
            
            return RasterInfo(...)
    
    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            f"Cannot open '{uri}'. Ensure file exists and is a valid raster. "
            f"Supported formats: GeoTIFF, COG, PNG, JPEG, NetCDF."
        ) from e
```

### Processing Tools (convert, reproject)

```python
async def reproject_raster(
    uri: str,
    output: str,
    params: ReprojectionParams,
    ctx: Context | None = None,
) -> ReprojectionResult:
    """Reproject with progress reporting."""
    
    if ctx:
        await ctx.info(f"📂 Opening raster: {uri}")
    
    with rasterio.open(uri) as src:
        if ctx:
            await ctx.info(
                f"✓ Source: {src.crs}, {src.width}x{src.height}, {src.count} bands"
            )
            await ctx.report_progress(0, 100)
        
        # Calculate transform...
        
        if ctx:
            await ctx.info(f"📐 Output size: {dst_width}x{dst_height}")
        
        with rasterio.open(output, "w", **profile) as dst:
            for band_idx in range(1, src.count + 1):
                if ctx:
                    progress = int((band_idx / src.count) * 100)
                    await ctx.report_progress(progress, 100)
                    await ctx.debug(f"Processing band {band_idx}/{src.count}")
                
                reproject(...)
        
        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(f"✓ Reprojection complete: {output}")
    
    return ReprojectionResult(...)
```

## Consequences

**Positive**:
- ✅ **Superior UX** - Users know what's happening
- ✅ **LLM transparency** - LLMs can explain process to users
- ✅ **Debugging** - Structured logging helps diagnose issues
- ✅ **Production quality** - Follows MCP best practices
- ✅ **Testability** - Context optional, tools work without it

**Negative**:
- ⚠️ **Code verbosity** - More lines per tool (30-40% increase)
- ⚠️ **If-ctx checks** - Repetitive `if ctx:` guards
- ⚠️ **Testing overhead** - Need to verify Context behavior

**Neutral**:
- Tools callable with or without Context
- Progressive enhancement (works without, better with)

## Alternatives Considered

**1. Silent execution (current MVP)**
- ❌ Rejected: Poor UX on long operations
- ❌ Rejected: Not MCP best practice

**2. Required Context parameter**
```python
async def tool(uri: str, ctx: Context) -> Result:
```
- ❌ Rejected: Breaks testability
- ❌ Rejected: Harder to use in non-MCP contexts

**3. Callback-based progress**
```python
async def tool(uri: str, on_progress: Callable) -> Result:
```
- ❌ Rejected: Not MCP-native
- ❌ Rejected: Doesn't integrate with FastMCP

## Related

- **ADR-0021**: LLM-Optimized Tool Descriptions - Complements Context with discoverability
- **FastMCP Guidelines**: Context capabilities (logging, progress, sampling)
- **MCP Spec**: Progress reporting, logging primitives

## Migration Path

**Phase 1** (This ADR): Add Context to all tools
**Phase 2** (ADR-0021): Enhance descriptions and safety hints
**Phase 3**: Add decision-tree prompts

Existing tools continue to work; Context provides progressive enhancement.

## References

- [FastMCP Context Documentation](https://gofastmcp.com)
- [MCP Specification - Logging](https://modelcontextprotocol.io)
- MCP Best Practice: "Use Context for transparency and UX"
