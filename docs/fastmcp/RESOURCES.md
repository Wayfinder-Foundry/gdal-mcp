# FastMCP Resources Deep Dive

**Status**: Technical Guide  
**Last Updated**: 2025-10-07  
**Purpose**: Understand `@mcp.resource()` and its role in agentic geospatial reasoning

---

## What Are MCP Resources?

**MCP Resources are read-only data sources that AI agents can access to gather context, reference information, and supporting data.**

Think of them as **knowledge repositories**:
- Background information to inform decisions
- Reference data to guide analysis
- Context to understand the problem space
- Documentation to learn methodologies

### Key Concept

```
Resources = Information the AI can READ
Tools = Actions the AI can EXECUTE
Prompts = Guidance on how to THINK
```

---

## The Three Pillars

| Aspect | Resources | Tools | Prompts |
|--------|-----------|-------|---------|
| **Purpose** | Provide information | Execute actions | Guide thinking |
| **Direction** | AI reads from | AI writes to | AI reasons with |
| **Nature** | Read-only data | Read-write operations | Message templates |
| **Example** | CRS reference | Reproject raster | Choose CRS guide |

---

## Why Resources Are Crucial for Our Vision

### 1. Domain Knowledge Access

**Without Resources:**
```
User: "Reproject this DEM"
AI: → Asks for target CRS
```

**With Resources:**
```python
@mcp.resource("reference://common-crs-by-region")
def get_crs_reference() -> dict:
    return {
        "North America": {"web": "EPSG:3857", "utm": "varies"},
        "Europe": {...}
    }
```
```
AI: → Reads CRS reference
    → Chooses EPSG:3857 for web map
    → No user question needed
```

### 2. Workspace Awareness

```python
@mcp.resource("workspace://datasets")
def list_workspace_datasets() -> dict:
    """Discover all available datasets."""
    return {"datasets": discover_all_datasets()}
```

**Result**: AI knows what data exists without asking

### 3. Analysis Context

```python
@mcp.resource("history://recent-operations")
def get_recent_ops() -> list:
    """Log of recent processing operations."""
    return recent_processing_history()
```

**Result**: AI understands previous work, can continue workflows

---

## Resource Types

### 1. Reference Resources (Static)

```python
@mcp.resource("reference://crs-guide")
def crs_guide() -> dict:
    return {
        "geographic": {"EPSG:4326": "WGS 84 Global"},
        "projected": {"EPSG:3857": "Web Mercator"}
    }
```

### 2. Metadata Resources (Dynamic)

```python
@mcp.resource("metadata://{dataset}/info")
def get_dataset_metadata(dataset: str) -> dict:
    with rasterio.open(find_dataset(dataset)) as src:
        return {
            "crs": str(src.crs),
            "bounds": src.bounds,
            "resolution": src.res
        }
```

### 3. Catalog Resources

```python
@mcp.resource("catalog://available-datasets")
def get_catalog() -> dict:
    return {
        "datasets": {
            name: extract_metadata(path)
            for name, path in discover_datasets()
        }
    }
```

### 4. State Resources

```python
@mcp.resource("state://current-analysis")
def get_current_state() -> dict:
    return {
        "last_operation": get_last_op(),
        "workspace": get_current_workspace(),
        "pending_tasks": get_pending()
    }
```

---

## Geospatial Examples

### Example 1: CRS Information Service

```python
@mcp.resource("crs://details/{epsg_code}")
def get_crs_details(epsg_code: str) -> dict:
    """Detailed CRS information from EPSG code."""
    from pyproj import CRS
    crs = CRS.from_epsg(int(epsg_code))
    
    return {
        "epsg_code": epsg_code,
        "name": crs.name,
        "type": crs.type_name,
        "is_projected": crs.is_projected,
        "area_of_use": crs.area_of_use.name if crs.area_of_use else None,
        "units": crs.axis_info[0].unit_name
    }
```

### Example 2: Terrain Analysis Parameters

```python
@mcp.resource("reference://terrain-parameters")
def get_terrain_params() -> dict:
    """Reference for terrain analysis parameters."""
    return {
        "slope": {
            "algorithms": {
                "horn": "3x3 Horn (standard)",
                "zevenbergen_thorne": "Smoothed for noise"
            },
            "classification": {
                "flat": "0-2°", "gentle": "2-5°",
                "moderate": "5-15°", "steep": ">15°"
            }
        },
        "aspect": {
            "range": "0-360° (0=North, clockwise)",
            "flat_value": -1
        }
    }
```

### Example 3: Geospatial Glossary

```python
@mcp.resource("reference://glossary")
def get_glossary() -> dict:
    """Domain terminology reference."""
    return {
        "CRS": {
            "full_name": "Coordinate Reference System",
            "definition": "Framework for measuring locations",
            "types": ["Geographic", "Projected"],
            "related": ["EPSG", "WKT", "Proj4"]
        },
        "DEM": {
            "full_name": "Digital Elevation Model",
            "uses": ["Terrain analysis", "Watershed", "Viewshed"],
            "related": ["DTM", "DSM"]
        }
    }
```

### Example 4: Recommended Workflows

```python
@mcp.resource("workflows://recommended/{analysis_type}")
def get_workflow(analysis_type: str) -> dict:
    """Step-by-step workflow guidance."""
    workflows = {
        "slope_analysis": {
            "steps": [
                {"action": "Verify DEM", "tool": "raster_info"},
                {"action": "Compute slope", "parameters": {"method": "horn"}},
                {"action": "Statistics", "tool": "raster_stats"}
            ]
        }
    }
    return workflows.get(analysis_type, {})
```

### Example 5: Processing History

```python
@mcp.resource("history://processing-log")
def get_history() -> list:
    """Recent processing operations log."""
    return [
        {
            "timestamp": "2025-10-07T14:30:00",
            "operation": "raster_reproject",
            "input": "/data/dem.tif",
            "output": "/results/dem_utm.tif",
            "parameters": {"target_crs": "EPSG:32610"}
        }
    ]
```

---

## Best Practices

### 1. Clear URI Schemes

✅ **Good**:
```python
@mcp.resource("reference://crs/geographic")
@mcp.resource("catalog://datasets/raster")
@mcp.resource("metadata://{dataset}/spatial")
```

❌ **Bad**:
```python
@mcp.resource("resource://data1")
@mcp.resource("resource://stuff")
```

### 2. Rich Metadata

```python
@mcp.resource(
    uri="reference://resampling-methods",
    name="Resampling Methods Guide",
    description="Complete resampling reference",
    tags={"reference", "raster"},
    meta={"version": "1.0"}
)
def get_resampling_guide() -> dict:
    return {...}
```

### 3. Cache Expensive Operations

```python
import functools

@functools.lru_cache(maxsize=1)
def _scan_datasets_cached(cache_key: int):
    return expensive_scan()

@mcp.resource("catalog://datasets")
def get_catalog() -> dict:
    cache_key = int(time.time() / 300)  # 5 min cache
    return _scan_datasets_cached(cache_key)
```

### 4. Handle Errors Gracefully

```python
@mcp.resource("metadata://{dataset}/info")
def get_metadata(dataset: str) -> dict:
    try:
        return extract_metadata(dataset)
    except FileNotFoundError:
        return {
            "error": "Dataset not found",
            "available": list_available_datasets()
        }
```

### 5. Provide Context, Not Just Data

✅ **Good**:
```python
return {
    "dataset": "dem.tif",
    "analysis_date": "2025-10-07",
    "statistics": {"min": 100, "max": 500},
    "units": "meters",
    "interpretation": "Mountainous terrain"
}
```

❌ **Bad**:
```python
return {"min": 100, "max": 500}
```

---

## Resource Hierarchy

```
reference://                  # Static reference
├── crs/guide
├── terrain/parameters
└── glossary

catalog://                    # Dataset discovery
├── datasets/raster
└── datasets/vector

metadata://                   # Dynamic metadata
└── {dataset}/spatial

workspace://                  # Workspace info
├── datasets
└── configuration

history://                    # Processing log
└── recent-operations

state://                      # Current state
└── analysis-context
```

---

## Action Items for gdal-mcp

### Immediate (This Week)

1. **Create first resources**:
```python
@mcp.resource("workspace://datasets")
@mcp.resource("reference://crs-common")
```

2. **Test with Claude Desktop**:
   - Verify AI can discover and use resources
   - Iterate on structure

### Short-term (This Month)

3. **Add domain resources**:
   - Terrain analysis parameters
   - Resampling method guide
   - CRS selection guide

4. **Build catalog resources**:
   - Dataset discovery
   - Workspace inventory
   - Format support matrix

### Long-term (This Quarter)

5. **Complete resource ecosystem**:
   - Processing history
   - Workflow templates
   - Analysis results

6. **Documentation**:
   - Resource discovery guide
   - URI scheme reference
   - Examples in QUICKSTART

---

## Conclusion

**Resources give AI agents the knowledge infrastructure to operate autonomously.**

Without resources, AI agents:
- Ask repetitive questions
- Make uninformed decisions
- Operate in isolation

With resources, AI agents:
- Self-educate from references
- Discover available data
- Understand workspace context
- Make informed decisions
- Continue multi-step workflows

**This transforms gdal-mcp from "command executor" to "informed geospatial assistant."**

---

## References

- **FastMCP Docs**: [Resources Guide](https://github.com/jlowin/fastmcp/blob/main/docs/servers/resources.mdx)
- **VISION.md**: Long-term goals
- **PROMPTS_DEEP_DIVE.md**: How prompts guide reasoning
- **MCP Spec**: [Resources](https://spec.modelcontextprotocol.io/specification/server/resources/)

---

*"Knowledge is power. Resources give AI agents knowledge."*
