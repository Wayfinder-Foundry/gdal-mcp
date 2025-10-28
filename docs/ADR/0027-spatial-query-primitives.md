# ADR-0027: Conversational Spatial Query Layer

**Status:** Proposed  
**Date:** 2025-10-27  
**Deciders:** Core Team  
**Related:** ADR-0017 (Python-native), ADR-0026 (Reflection System)

---

## Context

### The Symbiotic Analyst-Agent Vision

**Target use case:** An analyst asks a domain question:
> "How much of this satellite image is urban area?"

To answer this, the agent must:
1. Sample spatial regions (query subsets)
2. Analyze spectral signatures (classification)
3. Calculate area statistics (aggregation)
4. Refine iteratively based on results

**Current limitation:** GDAL MCP v1.1 only provides **file-centric operations** (process entire files). The agent cannot:
- Query spatial subsets for analysis
- Iteratively refine query extents
- Compose multi-step spatial workflows
- Answer analytical questions through spatial exploration

### The Gap We're Filling

**GDAL already has spatial operations:**
- `gdal.Warp -te` (clip to extent)
- Rasterio windowed reading (`.read(window=...)`)
- pyogrio spatial filtering (`bbox=...`)

**What's missing: Conversational interface + intelligent composition**
- Natural language → appropriate GDAL operation
- Reflection/justification for spatial reasoning
- Automatic optimization detection
- Workflow orchestration across queries

**We're not reimplementing GDAL. We're making it conversational.**

### Real-World Use Case: LiDAR QC Analysis

**Scenario:** A geomatics analyst needs to perform intraswath accuracy testing (smooth-surface repeatability) for LiDAR calibration quality control.

**Required workflow:**
1. Identify candidate flat surfaces (airstrips, parking lots) from DEM or orthophoto
2. Define bounding geometry around identified surface
3. **Extract point cloud subset** from large LAS/LAZ file using spatial query
4. Analyze surface variation for calibration metrics

**Current limitation:** Step 3 requires either:
- Processing the entire multi-GB point cloud file
- Manually pre-clipping files (breaks workflow continuity)
- External tools outside GDAL MCP (defeats integrated reasoning)

**Broader implication:** Many geospatial workflows require **spatial random access**, not sequential file processing.

### The Analyst-Agent Symbiosis Vision

**Current state:** Agent executes analyst's explicit commands
```
Analyst: "Reproject this DEM to UTM Zone 10N"
Agent: *executes specific tool*
Result: File transformed as requested
```

**Desired state:** Agent and analyst explore spatially together
```
Analyst: "I need to find flat surfaces in this DEM for calibration QC"
Agent: "I can query spatial subsets and calculate slope. Where should I search?"
Analyst: "Try near these coordinates - likely airstrip locations"
Agent: *queries DEM subset → calculates slope → identifies candidates*
       "Found 3 flat surfaces with <2° slope, here are their geometries"
Analyst: "The middle one is the airstrip. Extract points from that area."
Agent: *spatial query on point cloud → extracts subset → analyzes variation*
```

**Key insight:** The agent brings **pattern discovery** and **tool knowledge**. The analyst brings **real-world context** and **domain constraints**. Spatial querying enables their collaboration.

---

## Decision

**We will create a conversational layer over existing GDAL spatial operations**, enabling:
1. Natural language → GDAL spatial query mapping
2. Reflection/justification for spatial reasoning
3. Iterative refinement through dialogue
4. Compositional workflows (query → analyze → refine → query)

**This shifts GDAL MCP from "execute commands" to "answer analytical questions."**

**Critical scope decision:**
- ✅ **We wrap existing GDAL/Rasterio/pyogrio functionality**
- ❌ **We do NOT reimplement spatial operations**
- ✅ **We add conversational interface + methodological justification**
- ❌ **We do NOT create custom indexing or virtual dataset logic** (see ADR-0028, ADR-0029)

---

## Rationale

### 1. Foundation for Advanced Workflows

**All analysis tools benefit from spatial subsets:**
- Slope analysis on specific terrain features (not entire DEM)
- Zonal statistics within dynamic boundaries (not predefined zones)
- Multi-temporal change detection on overlapping areas (not full scenes)

**Spatial query unlocks compositional workflows:**
```
Query region → Analyze → Discover pattern → Query refined region → Analyze deeper
```

### 2. Enables AI Pattern Discovery

**Without spatial query:**
- AI can only operate on entire files
- Pattern discovery limited to metadata inspection
- No exploratory spatial sampling

**With spatial query:**
- AI can sample regions to understand spatial patterns
- Discover anomalies through iterative spatial refinement
- Test hypotheses by querying specific geometries

**Example:** AI could discover that slope variation patterns differ between north-facing and south-facing slopes by querying and comparing multiple oriented regions.

### 3. Python-Native Implementation is Natural

Our ADR-0017 Python-native stack already supports spatial queries:
- **Rasterio:** Window-based reading with spatial indexing
- **pyogrio:** SQL-like spatial filtering, bounding box queries
- **Shapely:** Geometric operations for query polygon validation

**No new dependencies required** - we're exposing existing capabilities.

### 4. Complements Reflection System

Spatial queries have methodological implications:
- **Query extent choice:** Why this area? What properties must it have?
- **Sampling strategy:** Random? Systematic? Stratified?
- **Resolution tradeoffs:** Full resolution query vs downsampled preview?

**Reflection prompts can guide query reasoning**, extending epistemic governance to spatial exploration.

---

## Architecture

### Core Principle: Wrap, Don't Rewrite

**We provide a conversational interface over existing GDAL capabilities:**
- Rasterio for raster spatial queries
- pyogrio for vector spatial queries
- Reflection middleware for methodological justification
- MCP resources for query result inspection

### Spatial Query Tools

#### `raster_query` - Conversational Raster Windowing

**Wraps:** Rasterio windowed reading (`rasterio.open().read(window=...)`)

```python
@mcp.tool()
async def raster_query(
    uri: str,
    geometry: dict | list[float],  # GeoJSON polygon or bbox
    output: str | None = None,      # None = in-memory for composition
    bands: list[int] | None = None,
    ctx: Context | None = None
) -> Result:
    """Query raster by spatial extent.
    
    This is a conversational wrapper around Rasterio window reading.
    
    Value-add:
    - Reflection for query extent justification
    - Natural language → spatial extent mapping
    - Result as MCP resource for composition
    - Progress reporting for large queries
    """
    # Reflection: Justify query extent
    # Implementation: Pure Rasterio (no custom logic)
    # Return: MCP resource for next operation
```

**Implementation:**
```python
with rasterio.open(uri) as src:
    window = from_bounds(*bounds, src.transform)
    data = src.read(bands=bands, window=window)
    
    if output:
        # Persist for inspection
        write_result(output, data, src.meta)
    else:
        # In-memory for immediate composition
        return InMemoryResult(data, metadata)
```

#### `vector_query` - Conversational Vector Filtering

**Wraps:** pyogrio spatial filtering (`read_dataframe(bbox=...)`)

```python
@mcp.tool()
async def vector_query(
    uri: str,
    geometry: dict | list[float],
    output: str | None = None,
    attributes: list[str] | None = None,
    where: str | None = None,
    ctx: Context | None = None
) -> Result:
    """Query vector by spatial/attribute filters.
    
    This is a conversational wrapper around pyogrio filtering.
    
    Value-add:
    - Reflection for query reasoning
    - Natural language → SQL filter mapping
    - Result as MCP resource
    - Multi-criteria filtering guidance
    """
    # Reflection: Justify query criteria
    # Implementation: Pure pyogrio (no custom logic)
    # Return: MCP resource
```

**Implementation:**
```python
gdf = read_dataframe(
    uri,
    bbox=bbox,
    where=where,
    columns=attributes
)

if output:
    gdf.to_file(output)
else:
    return InMemoryGeoDataFrame(gdf)
```

### Optimization Considerations (Out of Scope for v1.2.0)

**Phase 3a (this ADR) focuses on core conversational wrapper only.**

**Optimization capabilities deferred to future ADRs:**
- **Spatial indexing** → ADR-0028 (detection, creation, usage)
- **VRT management** → ADR-0029 (multi-file query optimization)
- **Advanced caching** → Future consideration

**Rationale for deferral:**
1. Core spatial query works WITHOUT optimization (just slower)
2. Optimization adds significant complexity
3. Need usage data to inform optimization heuristics
4. Keeps v1.2.0 scope manageable

**Note:** Existing GDAL/Rasterio/pyogrio optimizations (GeoPackage R-tree, COG tiling, Shapefile .shx) are used automatically - we don't need custom implementations for basic performance.

#### In-Memory Results for Composition (In Scope)

**Purpose:** Enable immediate composition without disk I/O

**When to use in-memory:**
```python
if next_operation_imminent:
    return InMemoryResult()  # Agent can chain immediately
else:
    persist_to_disk()  # Human inspection + provenance
```

**Implementation:**
- Rasterio `MemoryFile` for rasters
- GeoDataFrame in memory for vectors
- Lifetime: Single workflow session only

**Self-Review Pattern:**
When in-memory result created, trigger lightweight reflection:
```
"You've created an intermediate result (in-memory raster, 1024×1024, 3 bands).
 This will feed into [next operation]. Does this make sense for your workflow?"
```

Agent self-reviews:
- Are dimensions/attributes as expected?
- Is this appropriate for the next operation?
- Should this be persisted for inspection instead?

**Benefits:**
- Maintains audit trail via reasoning (not data persistence)
- Agent self-corrects if intermediate result looks wrong
- Aligns with "trust the model, but verify through reflection" philosophy
- No need to enumerate all possible intermediate states

---

## MCP Integration

### Tools (Stateful Operations)

**Query tools (Phase 3a - v1.2.0):**
```python
raster_query(uri, geometry, ...)  # Conversational raster windowing
vector_query(uri, geometry, ...)  # Conversational vector filtering
```

**Future tools (deferred to ADR-0028, ADR-0029):**
- Index management: `spatial_index_create`, `spatial_index_delete`
- VRT management: `vrt_create`, `vrt_delete`

### Resources (Discoverable Metadata)

**Query results (Phase 3a):**
```
query://result/{query_id}
├── geometry_used: [...]
├── bands: [1, 2, 3]
├── pixel_count: 1048576
├── size_bytes: 12582912
└── created: "2025-10-27T14:00:00Z"
```

**Future resources (deferred):**
- `index://dataset.tif` - Index discovery
- `vrt://workspace/{pattern}` - VRT recommendations

### Prompts (Reflection/Justification)

**Phase 3a prompts:**
```python
justify_query_extent(geometry, purpose)
# - Why this spatial extent?
# - What properties must the area satisfy?
# - Alternatives considered?
```

**No prompts for optimization** (indexing/VRTs are performance, not methodology)

---

## Reflection Integration

### Query Methodology Prompts

**New reflection domain: `spatial_query`**

**Prompt: `justify_query_extent`**
- **Intent:** What spatial property must the query area satisfy?
- **Alternatives:** Why this geometry instead of broader/narrower extent?
- **Tradeoffs:** Resolution vs coverage, processing time vs detail

**Example:**
```
User: "Query this DEM for flat surfaces"
AI: *reflection: Why search this 10km² area?*
    Intent: Identify calibration targets (airstrips, parking lots)
    Alternative: Full DEM scan → rejected, computationally expensive
    Alternative: Predefined AOI → rejected, may miss candidates
    Choice: Query near known infrastructure (roads, buildings)
    Tradeoff: May miss remote flat surfaces, acceptable for this QC purpose
```

**Cache behavior:** Query extent justifications cached by geometry + purpose, not by dataset.

---

## Consequences

### Positive

1. **Enables analytical questions** - "How much urban area?" becomes answerable through spatial sampling
2. **Analyst-agent symbiosis** - Agent brings tool knowledge, analyst brings domain context
3. **Maintains Python-native architecture** - Just wraps existing Rasterio/pyogrio (no new dependencies)
4. **Simple implementation** - No custom spatial algorithms, minimal complexity
5. **Natural composition** - Query → analyze → refine workflows emerge naturally
6. **Foundation for optimization** - Usage patterns will inform ADR-0028/0029 heuristics

### Negative

1. **Limited scope** - No optimization in v1.2.0 (queries may be slow on large datasets)
2. **Memory management** - In-memory results require careful lifecycle management
3. **Error handling** - Geometry validation, out-of-bounds queries need robust handling
4. **Testing burden** - Need realistic spatial fixtures and multi-query workflows

### Risks

1. **Performance expectations** - Users may expect automatic optimization (not in v1.2.0)
2. **Memory leaks** - In-memory results not properly cleaned up → resource exhaustion
3. **Scope creep** - Pressure to add indexing/VRT before usage patterns are understood

**Mitigations:**
- **Clear documentation:** v1.2.0 is core capability only, optimization comes in v1.3+
- **Context managers:** Explicit lifecycle for in-memory resources
- **Usage monitoring:** Collect data to inform ADR-0028/0029 optimization decisions
- **Resist scope creep:** Implement, test, gather data BEFORE optimizing

---

## Implementation Phases

### Phase 3a: Conversational Spatial Query (v1.2.0) - This ADR

**Scope:** Core query tools only, defer optimization to future ADRs

**Milestones:**

**M1: Raster Query Tool**
- `raster_query(uri, geometry, output=None, bands, ctx)`
- Wrap Rasterio window reading
- In-memory result support for composition
- Error handling (invalid geometry, out-of-bounds)
- Progress reporting via Context API

**M2: Vector Query Tool**
- `vector_query(uri, geometry, output=None, attributes, where, ctx)`
- Wrap pyogrio spatial/attribute filtering
- In-memory GeoDataFrame support
- SQL-like filtering guidance
- Progress reporting

**M3: Query Result Resources**
- `query://result/{id}` resource for result inspection
- Metadata exposure (geometry used, size, created)
- Enable workflow composition

**M4: Reflection Integration**
- `justify_query_extent` prompt implementation
- Cache strategy for query justifications
- Lightweight self-review for in-memory results
- Testing with multi-query workflows

**Timeline:** 2-3 weeks

### Phase 3b: Optimization Discovery (v1.3.0) - ADR-0028

**Deferred:** Spatial indexing detection, creation, management

### Phase 3c: VRT Intelligence (v1.4.0) - ADR-0029

**Deferred:** Virtual dataset recommendation and management

### Phase 3d: Workflow Orchestration (v1.5.0+)

**Future:** Composition patterns, provenance tracking, pattern libraries

---

## Alternative Approaches Considered

### Alternative 1: Whole-File Tools Only (Status Quo)

**Approach:** Maintain file I/O focus, require pre-processing for spatial subsets

**Rejected because:**
- Breaks workflow continuity (manual pre-clipping required)
- Defeats agentic reasoning (agent can't explore spatially)
- Doesn't unlock analyst-agent symbiosis

### Alternative 2: Resource-Only Pattern

**Approach:** Expose spatial queries as MCP resources instead of tools
```
query://dataset.tif?bbox=[...]&bands=[1,2,3]
```

**Rejected because:**
- Resources are read-only (can't create indexes, persist results)
- Harder to integrate with reflection system (tools support pre-execution prompts)
- Less flexible for result management (in-memory vs persisted)

**Potential future hybrid:** Resources for discovery, tools for execution

### Alternative 3: Reimplementing Spatial Operations

**Approach:** Build custom spatial query engine from scratch

**Rejected because:**
- **Reinventing the wheel:** Rasterio/pyogrio already provide excellent spatial query
- **Maintenance burden:** Custom implementations require ongoing optimization and bug fixes
- **Limited value-add:** Our unique value is conversational interface, not faster spatial operations
- **Risk of bugs:** Spatial operations are complex; existing libraries are battle-tested

**Decision:** Wrap existing libraries, focus on conversational layer

**This is the critical architectural insight:** We're not a GDAL replacement. We're a GDAL conversation layer.

### Alternative 4: External Indexing Service

**Approach:** Separate microservice for spatial indexing (PostGIS-like)

**Rejected because:**
- Violates ADR-0017 Python-native principle
- Adds deployment complexity (now multi-service architecture)
- Increases latency (network overhead for every query)

**However:** For very large datasets (>1 TB), external indexing may become necessary. Defer until proven need.

---

## References

- **ADR-0017:** Python-Native Implementation Strategy
- **ADR-0026:** Reflection System and Epistemic Governance
- **docs/VISION.md:** Phase 3 - Workflow Intelligence
- **Rasterio windowed reading:** https://rasterio.readthedocs.io/en/stable/topics/windowed-rw.html
- **pyogrio spatial filtering:** https://pyogrio.readthedocs.io/en/latest/geopandas.html#spatial-filtering

---

## Next Steps

### Documentation (Immediate)

1. **Create ADR-0028 stub** - Spatial Indexing Strategy (outline only, defer details)
2. **Create ADR-0029 stub** - VRT Management (outline only, defer details)
3. **Update VISION.md** - Reflect Phase 3a/3b/3c split
4. **Create CONFIGURATION.md** - Centralize env var documentation (separate from ADRs)

### Implementation (Phase 3a - v1.2.0)

5. **Create spatial query fixtures** - Small test datasets (10×10 rasters, simple vectors)
6. **Implement `raster_query` tool** - Wrap Rasterio windows, add reflection
7. **Implement `vector_query` tool** - Wrap pyogrio filtering, add reflection
8. **Define `justify_query_extent` prompt** - Spatial reasoning reflection
9. **Implement query result resources** - `query://result/{id}` handlers
10. **Write integration tests** - Multi-query workflows, cache behavior, composition

### Validation

11. **Test with analytical questions** - "How much urban area in this image?"
12. **Document usage patterns** - Inform ADR-0028/0029 optimization decisions

---

**Author:** GDAL MCP Core Team  
**Reviewers:** TBD  
**Approval Date:** TBD
