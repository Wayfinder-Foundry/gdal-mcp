# ADR-0019: Parallel Processing Strategy for Large Geospatial Datasets

**Status**: Proposed (Future Implementation)  
**Date**: 2025-09-30  
**Deciders**: Jordan Godau  
**Tags**: #performance #dask #rioxarray #scalability #future

## Context

As GDAL MCP expands beyond MVP metadata operations into complex processing workflows, **processing time becomes a critical UX challenge**. MCP interactions feel frustrating when operations take minutes instead of seconds.

**Current constraints**:
- MCP clients expect sub-minute response times for good UX
- Geospatial processing is inherently compute/IO intensive
- Single-threaded Python is insufficient for large datasets (>1GB rasters, >1M vector features)
- Users will expect cloud-native operations on COGs, S3 data, etc.

**Problem statement**: How do we enable fast processing of large geospatial datasets within MCP's interactive time constraints?

## Decision

**Adopt Dask for parallel geospatial processing** when datasets exceed interactive thresholds:

1. **Raster operations** → `dask` + `rioxarray` (xarray with rasterio backend)
2. **Vector operations** → `dask-geopandas` (partitioned GeoDataFrames)
3. **Threshold-based activation** → Use parallel path only for large datasets
4. **Local Dask client** → Start in-process for simplicity, scale to distributed later

## Strategy

### Raster Processing: dask + rioxarray

**Current (MVP)**: Rasterio loads entire raster into memory
```python
with rasterio.open(uri) as src:
    data = src.read()  # Entire array in RAM
    stats = compute_stats(data)
```

**Future (Dask)**: Lazy evaluation with chunked processing
```python
import rioxarray as rxr
import dask.array as da

# Open lazily (no read yet)
raster = rxr.open_rasterio(uri, chunks={'x': 2048, 'y': 2048})

# Compute on chunks in parallel
stats = raster.mean().compute()  # Dask scheduler parallelizes

# COG/Cloud-native support
raster = rxr.open_rasterio('s3://bucket/cog.tif', chunks='auto')
```

**Benefits**:
- ✅ Out-of-core processing (doesn't require full dataset in RAM)
- ✅ Parallel computation across chunks
- ✅ Native COG/cloud support (reads only needed tiles)
- ✅ Lazy evaluation (only compute what's needed)

### Vector Processing: dask-geopandas

**Current (MVP)**: GeoPandas loads entire dataset
```python
gdf = gpd.read_file(uri)  # Entire dataset in RAM
gdf_buffered = gdf.buffer(100)
```

**Future (Dask)**: Partitioned parallel processing
```python
import dask_geopandas as dgpd

# Read in partitions
dgdf = dgpd.read_file(uri, npartitions=8)

# Parallel operations
dgdf_buffered = dgdf.buffer(100)  # Computed per partition
result = dgdf_buffered.compute()  # Gather results
```

**Benefits**:
- ✅ Handles datasets too large for RAM
- ✅ Parallel spatial operations
- ✅ Compatible with existing geopandas code
- ✅ Automatic task graph optimization

### Threshold-Based Activation

**Not all operations need Dask** - overhead isn't worth it for small data:

| Dataset Size | Approach | Rationale |
|--------------|----------|-----------|
| **< 100 MB raster** | Pure rasterio | Fast enough, less overhead |
| **< 10K vector features** | Pure geopandas | In-memory is faster |
| **> 100 MB raster** | dask + rioxarray | Parallel chunks, out-of-core |
| **> 10K vector features** | dask-geopandas | Partitioned processing |
| **Cloud/COG** | Always dask | Lazy loading, tile-based reads |

**Implementation pattern**:
```python
async def process_raster_smart(uri: str, operation: str) -> Result:
    """Automatically choose single-threaded or parallel based on size."""
    size_mb = get_raster_size_mb(uri)
    
    if size_mb < 100 and not is_cloud_uri(uri):
        # Fast path: pure rasterio
        return await process_with_rasterio(uri, operation)
    else:
        # Parallel path: dask + rioxarray
        return await process_with_dask(uri, operation)
```

### Local Dask Client Strategy

**Start simple**: In-process client with thread pool
```python
from dask.distributed import Client, LocalCluster

# Start local cluster (per-request or singleton)
client = Client(LocalCluster(n_workers=4, threads_per_worker=2))

# Process with client
result = dask_computation.compute()
```

**Scale later**: Distributed cluster when needed
- External Dask scheduler for multi-machine
- Kubernetes-based Dask cluster
- Cloud-native Dask (AWS Fargate, GCP Cloud Run)

## Rationale

**Why Dask over alternatives**:

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Multiprocessing** | ✅ Python stdlib<br>✅ Simple | ❌ Pickling overhead<br>❌ No lazy evaluation<br>❌ Hard to scale | ❌ Insufficient |
| **Ray** | ✅ Powerful<br>✅ ML/AI ecosystem | ❌ Heavy dependency<br>❌ No native geospatial<br>❌ Overkill for MCP | ❌ Too complex |
| **Dask (chosen)** | ✅ Lazy evaluation<br>✅ Native xarray/pandas<br>✅ Out-of-core<br>✅ Scales to cluster<br>✅ Geospatial ecosystem | ⚠️ Learning curve<br>⚠️ Scheduler overhead | ✅ **Best fit** |

**Why rioxarray specifically**:
- Built on xarray (N-dimensional arrays with labels)
- Uses rasterio backend (GDAL under the hood)
- Native COG and cloud support
- Integrates seamlessly with Dask
- Used by NASA, USGS, climate science community

**UX impact**:
```
Without Dask:
- Process 10GB raster → 5-10 minutes → Frustrating ❌

With Dask (8 workers):
- Process 10GB raster → 30-60 seconds → Acceptable ✅
```

## Implementation Timeline

**Phase 1 (Post-MVP)**: Proof of concept
- Add dask, rioxarray, dask-geopandas as optional dependencies
- Implement one raster tool with Dask variant (e.g., `raster.stats_large`)
- Benchmark performance gains
- Document patterns

**Phase 2**: Threshold-based smart routing
- Implement size/type detection
- Auto-select serial vs parallel path
- Add progress reporting for long operations

**Phase 3**: Scale to distributed
- Support external Dask scheduler
- Kubernetes deployment guide
- Cloud-native examples (S3, GCS)

## Consequences

**Positive**:
- ✅ **Sub-minute processing** for multi-GB datasets
- ✅ **Cloud-native support** (COG, S3) without full downloads
- ✅ **Out-of-core** operations for datasets larger than RAM
- ✅ **Future-proof** for distributed/cluster scaling
- ✅ **Good citizen** in MCP ecosystem (responsive tools)

**Negative**:
- ⚠️ **Added complexity** - Dask has learning curve
- ⚠️ **Dependency weight** - ~50MB for dask + rioxarray
- ⚠️ **Scheduler overhead** - Not worth it for small data
- ⚠️ **Memory management** - Need to tune chunk sizes

**Neutral**:
- Optional dependencies (don't force on all users)
- Transparent to MCP clients (same tool interface)
- Can start with local client, scale to distributed later

## Alternatives Considered

**1. Stream processing (no Dask)**
- Process data in chunks manually
- ❌ Rejected: Reinventing Dask, more code

**2. External workers (separate processes)**
- Tools submit jobs to worker pool
- ❌ Rejected: More infrastructure, harder deployment

**3. Always use CLI tools (gdalwarp, ogr2ogr)**
- GDAL CLI has built-in threading
- ❌ Rejected: Loss of Python-native benefits (ADR-0017)

## Dependencies

**Add to pyproject.toml**:
```toml
[project.optional-dependencies]
parallel = [
    "dask[complete]>=2024.1",      # Parallel processing framework
    "rioxarray>=0.15",              # Xarray with rasterio backend
    "dask-geopandas>=0.3",          # Partitioned GeoDataFrames
    "distributed>=2024.1",          # Dask distributed scheduler
]
```

**Installation**:
```bash
# MVP (no parallel)
uv pip install gdal-mcp

# With parallel processing
uv pip install "gdal-mcp[parallel]"
```

## Performance Targets

| Operation | Dataset Size | Serial Time | Dask Time (8 workers) | Target |
|-----------|--------------|-------------|-----------------------|--------|
| Raster stats | 1 GB | 60s | 15s | < 30s ✅ |
| Raster reproject | 5 GB | 300s | 60s | < 90s ✅ |
| Vector buffer | 1M features | 120s | 30s | < 60s ✅ |
| COG stats (S3) | 10 GB | N/A (OOM) | 45s | < 60s ✅ |

## Related

- **ADR-0017**: Python-native over CLI - Enables this approach
- **ADR-0018**: Hybrid vector stack - GeoPandas → Dask-GeoPandas path
- **ADR-0015**: Benchmark suite - Will validate performance gains

## References

- [Dask Documentation](https://docs.dask.org)
- [rioxarray Documentation](https://corteva.github.io/rioxarray/)
- [Dask-GeoPandas Documentation](https://dask-geopandas.readthedocs.io)
- [Pangeo (Dask + Geospatial)](https://pangeo.io)
