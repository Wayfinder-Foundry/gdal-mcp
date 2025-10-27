# ADR-0027: Spatial Query Primitives as Phase 3 Foundation

**Status:** Proposed  
**Date:** 2025-10-27  
**Deciders:** Core Team  
**Related:** ADR-0017 (Python-native), ADR-0026 (Reflection System)

---

## Context

### The File I/O Limitation

GDAL MCP v1.1 provides comprehensive **file-centric operations**:
- `raster_info(file)` - Inspect entire file metadata
- `raster_reproject(input_file, output_file)` - Transform entire file
- `vector_clip(input_file, output_file, bounds)` - Process entire file with bounds

**What's missing:** The ability to **spatially query subsets** of datasets without full file processing.

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

**We will implement spatial query primitives as the foundation for Phase 3**, enabling:
1. Polygon-based spatial queries
2. Bounding box queries  
3. Conditional optimization (indexing, VRTs, in-memory drivers)
4. Query-driven workflows (not just file-to-file transformations)

**This shifts GDAL MCP from file I/O centric to spatially-aware.**

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

### Core Capabilities (Must-Have)

#### 1. Spatial Query Tools

**Raster spatial query:**
```python
raster_query(
    uri: str,
    geometry: dict | list[float],  # GeoJSON polygon or [minx, miny, maxx, maxy]
    output: str | None = None,     # If None, return in-memory
    bands: list[int] | None = None,
    resolution: list[float] | None = None
) -> Result
```

**Vector spatial query:**
```python
vector_query(
    uri: str,
    geometry: dict | list[float],  # GeoJSON polygon or bbox
    output: str | None = None,     # If None, return in-memory
    attributes: list[str] | None = None,
    where: str | None = None       # SQL-like attribute filter
) -> Result
```

**Key design decision:** `output=None` enables in-memory results for immediate follow-on operations.

#### 2. Implementation Strategy

**Raster queries (Rasterio):**
```python
# Window-based reading with spatial indexing
with rasterio.open(uri) as src:
    window = from_bounds(*bounds, transform=src.transform)
    data = src.read(window=window, out_shape=target_shape)
```

**Vector queries (pyogrio):**
```python
# Built-in spatial filtering
gdf = read_dataframe(
    uri,
    bbox=bbox,        # Spatial filter
    where=where_sql,  # Attribute filter
    columns=columns   # Column subset
)
```

**Both leverage native library optimizations** - no manual indexing needed for basic queries.

### Optimization Layer (Conditional)

#### 1. Spatial Indexing

**When to build spatial index:**
```python
# Decision heuristic
if dataset_size_gb > 10 and expected_query_count > 5:
    build_rtree_index()  # Amortize cost over multiple queries
```

**Index types:**
- **R-tree:** Vector datasets (Shapely STRtree)
- **Quadtree:** Raster datasets (tile-based indexing)

**Storage:** External sidecar files (`.idx`, `.qix`) for persistence

#### 2. Virtual Datasets (VRT)

**When to create VRT:**
```python
# Decision heuristic
if len(files) > 1 and are_spatially_contiguous(files) and query_spans_boundaries():
    create_vrt(files)  # Seamless querying across tiles
else:
    query_individual_files()  # Avoid VRT overhead
```

**Anti-pattern to avoid:**
- Creating VRT for spatially disjoint files (e.g., opposite sides of the world)
- VRT for single-query workflows (overhead not justified)

**VRT as tool vs resource:**
- **Tool:** `vrt_create(files, output)` - Explicit VRT generation
- **Resource:** `vrt://workspace/{pattern}` - Dynamic discovery (future consideration)

#### 3. In-Memory Drivers

**When to use memory driver:**
```python
# Decision heuristic  
if is_intermediate_result and next_operation_within_seconds < 30:
    use_memory_driver()  # Skip disk I/O
else:
    persist_to_disk()    # Provenance + resumability
```

**Implementation:**
- GDAL `/vsimem/` virtual file system
- Rasterio `MemoryFile` context managers
- Short-lived for pipeline operations only

**Trade-offs:**
- **Pro:** Eliminates I/O overhead in multi-step workflows
- **Con:** Results not directly inspectable (ephemeral)
- **Resolution:** Lightweight reflection for self-review

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

## Decision Framework: When to Optimize

### Flowchart for Query Optimization

```
Spatial Query Request
    ↓
Q: Will there be multiple queries on this dataset?
    ├─ No → Direct query (no index)
    └─ Yes → Q: Dataset > 10 GB?
            ├─ No → Direct query
            └─ Yes → Build spatial index
    ↓
Q: Does query span multiple files?
    ├─ No → Query single file
    └─ Yes → Q: Are files spatially contiguous?
            ├─ No → Query files individually
            └─ Yes → Create VRT, then query
    ↓
Q: Is result needed for immediate next operation?
    ├─ No → Persist to disk
    └─ Yes → Q: Next operation < 30 seconds away?
            ├─ No → Persist to disk
            └─ Yes → Use in-memory driver
```

### Configuration Parameters

Expose optimization thresholds as environment variables:
```bash
GDAL_MCP_INDEX_THRESHOLD_GB=10          # When to build spatial index
GDAL_MCP_INDEX_QUERY_COUNT=5            # Minimum queries to justify index
GDAL_MCP_MEMORY_DRIVER_TTL=30           # Seconds before persist in-memory
GDAL_MCP_VRT_MIN_FILES=2                # Minimum files for VRT consideration
```

**Rationale:** Different workflows have different optimization profiles. Make thresholds tunable.

**Configuration Management Note:**
This ADR exposes the need for comprehensive configuration management:
1. Centralized environment variable documentation (`docs/CONFIGURATION.md`)
2. Tiered configuration (static security boundaries vs dynamic operational settings)
3. Dynamic workspace switching (with user confirmation, within security boundaries)
4. Session-scoped vs persistent configuration

**Related future work:** Consider `workspace_switch` tool for dynamic workspace changes within allowed paths (requires explicit user confirmation for security).

---

## Tool vs Resource Design

### Spatial Query as Tools

**Rationale for tool-based design:**
1. **Stateful operation:** Query involves computation (reading, filtering, transforming)
2. **Reflection integration:** Queries may need methodological justification (extent choice, sampling strategy)
3. **Result management:** Tools can return in-memory or persisted outputs flexibly

**Example tools:**
- `raster_query(uri, geometry, ...)` → Query raster by spatial extent
- `vector_query(uri, geometry, ...)` → Query vector by spatial/attribute filters

### Spatial Indexes as Resources + Tools (Hybrid)

**Insight:** Indexes blur tool/resource boundaries - they're created (tool-like) but also discovered/inspected (resource-like).

**Proposed hybrid approach:**

#### Resources for Discovery & Inspection
```
index://dataset.tif
├── exists: true
├── type: "rtree"
├── path: "/workspace/.gdal_indexes/dataset.tif.spatial.idx"
├── created: "2025-10-27T14:00:00Z"
├── bounds: [...]
└── feature_count: 12450

index://dataset.tif/stats
├── query_count: 47
├── avg_query_time_ms: 12.3
└── cache_hit_rate: 0.73

index://dataset.tif/registry  # Multi-index support
├── spatial: "/path/to/dataset.tif.spatial.idx"
├── attributes:
│   ├── elevation: "/path/to/dataset.tif.attr_elevation.idx"
│   └── classification: "/path/to/dataset.tif.attr_classification.idx"
└── temporal: "/path/to/dataset.tif.temporal.idx"
```

#### Tools for Creation & Management
```python
spatial_index_create(uri, type="spatial") → creates index, returns resource URI
spatial_index_delete(uri, type="spatial") → removes index
spatial_index_rebuild(uri, type="spatial") → recreates if corrupt/outdated
```

#### Detection & Auto-Loading Pattern
```python
# Before spatial query execution
index_uri = f"index://{dataset_path}"
if resource_exists(index_uri):
    # Automatically load and use index
    use_spatial_index()
else:
    # Check if index creation justified
    if meets_threshold_criteria():
        prompt_index_creation()  # Lightweight suggestion
```

**Naming convention for uniqueness:**
```
.gdal_indexes/
├── dataset.tif.spatial.idx        # Spatial index (geometry-based)
├── dataset.tif.attr_elevation.idx # Attribute index (field-based)
├── dataset.tif.temporal.idx       # Temporal index (time-series)
```

**Benefits:**
- Resources enable automatic discovery (tools check for index before querying)
- Tools provide explicit control (create/delete/rebuild)
- Registry resource handles multi-index scenarios
- Unique naming prevents conflicts

### VRTs as Resources + Tools (Hybrid)

**Similar hybrid pattern:**

#### Resources for Discovery
```
vrt://workspace/project_tiles/
├── files: ["tile_1.tif", "tile_2.tif", "tile_3.tif"]
├── spatially_contiguous: true
├── recommended: true  # Meets VRT threshold criteria
└── coverage_bounds: [...]
```

#### Tools for Creation
```python
vrt_create(files, output) → Explicit VRT generation with validation
vrt_delete(vrt_path) → Remove VRT
```

#### Auto-Detection Pattern
```python
# When query spans multiple files
files = discover_files_in_query_extent()
vrt_resource = f"vrt://workspace/{pattern}"
if resource_exists(vrt_resource) and files_are_contiguous():
    use_existing_vrt()
else:
    query_files_individually()
```

**Decision:** Start with tool-based creation, add resource discovery in Phase 3b as usage patterns emerge.

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

1. **Unlocks real-world workflows** that require spatial subsetting (QC analysis, ROI extraction, multi-scale analysis)
2. **Enables AI pattern discovery** through iterative spatial sampling
3. **Maintains Python-native architecture** (no new dependencies)
4. **Natural composition** with existing tools (query → analyze → query → refine)
5. **Foundation for Phase 3b** (workflow orchestration builds on spatial primitives)

### Negative

1. **Complexity increase** in deciding when to optimize (indexing, VRT, in-memory)
2. **Memory management** becomes critical for in-memory operations
3. **Error handling** more complex (partial queries, invalid geometries, index failures)
4. **Testing burden** increases (need spatial test fixtures, optimization scenarios)

### Risks

1. **Over-optimization:** Building indexes/VRTs that aren't used → wasted computation
2. **Memory leaks:** In-memory drivers not properly cleaned up → resource exhaustion
3. **Confusion:** Users uncertain when to use spatial query vs whole-file tools

**Mitigations:**
- Conservative optimization defaults (prefer simple over optimized)
- Explicit in-memory driver lifecycle management (context managers)
- Clear documentation: "Use spatial query when you need a subset, whole-file tools otherwise"

---

## Implementation Phases

### Phase 3a: Spatial Query Primitives (v1.2.0)

**Milestone 1: Core Query Tools**
- `raster_query` - Polygon/bbox queries with Rasterio windows
- `vector_query` - Spatial/attribute filtering with pyogrio
- In-memory result support (`output=None`)
- Basic error handling (invalid geometries, out-of-bounds)

**Milestone 2: Optimization Layer**
- `spatial_index_create` tool (R-tree for vectors, quadtree for rasters)
- Decision heuristics for automatic indexing (configurable thresholds)
- Performance benchmarks (indexed vs non-indexed queries)

**Milestone 3: VRT Support**
- `vrt_create` tool for multi-file datasets
- Contiguity detection logic
- Query across VRT validation

**Milestone 4: Reflection Integration**
- `justify_query_extent` prompt
- Cache strategy for query justifications
- Testing with multi-query workflows

### Phase 3b: Workflow Intelligence (v1.3.0+)

**Builds on spatial query primitives:**
- Workflow composition (chain queries + analysis)
- Provenance tracking across spatial operations
- Pattern libraries (common query sequences)

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

### Alternative 3: External Indexing Service

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

1. **Draft Phase 3 implementation plan** (`docs/PHASE3_PLAN.md`)
2. **Update VISION.md** to reflect Phase 3a (spatial query) and 3b (workflow)
3. **Create configuration documentation** (`docs/CONFIGURATION.md`)
   - Centralize all environment variables
   - Document tiered configuration (static, dynamic, session)
   - Specify security boundaries and dynamic workspace switching
4. **Create spatial query fixtures** for testing (small raster/vector datasets)
5. **Prototype `raster_query` tool** with Rasterio window reading
6. **Define reflection prompts** for `justify_query_extent` and `intermediate_result_review`
7. **Implement index/VRT resource handlers** for discovery pattern
8. **Benchmark queries** (indexed vs non-indexed, in-memory vs disk)

---

**Author:** GDAL MCP Core Team  
**Reviewers:** TBD  
**Approval Date:** TBD
