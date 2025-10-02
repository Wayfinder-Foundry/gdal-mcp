# ADR-0018: Hybrid Vector Processing Stack (pyogrio + geopandas)

**Status**: Accepted  
**Date**: 2025-09-30  
**Deciders**: Jordan Godau  
**Tags**: #vector #geopandas #pyogrio #architecture

## Context

The MVP uses pyogrio (with fiona fallback) for vector operations. As we expand to vector processing and analysis, we need a strategy that balances:

1. **Performance** - Fast metadata operations and I/O
2. **Capability** - Rich spatial analysis and transformations
3. **Future scalability** - Support for parallel/distributed processing
4. **GDAL coverage** - Access to full GDAL vector functionality when needed

GeoPandas offers DataFrame-based vector processing with built-in spatial operations, but adds dependency weight and memory overhead. pyogrio is lightweight and fast for metadata operations.

## Decision

**Adopt a hybrid approach**:

1. **Use pyogrio for lightweight metadata operations**:
   - `vector.info` - Fast metadata extraction (current implementation)
   - Driver introspection
   - Layer enumeration
   - Bounds and CRS inspection

2. **Use geopandas for processing and analysis**:
   - `vector.reproject` - CRS transformations via `.to_crs()`
   - `vector.convert` - Format conversion via `.to_file()`
   - Spatial operations (buffer, join, overlay, clip)
   - Attribute filtering and transformations
   - Complex spatial analysis

3. **Use direct GDAL/OGR when needed**:
   - Advanced OGR features not in geopandas
   - Transactions and database operations
   - Direct SQL queries
   - Topology operations

## Rationale

**Why hybrid over single-stack**:

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **pyogrio only** | ✅ Lightweight<br>✅ Fast metadata<br>✅ Full GDAL coverage | ❌ No DataFrame API<br>❌ Limited analysis<br>❌ No Dask path | ❌ Not scalable |
| **geopandas only** | ✅ DataFrame API<br>✅ Rich operations<br>✅ Dask integration | ❌ Memory overhead<br>❌ Conversion cost<br>❌ Missing some OGR features | ⚠️ Good but wasteful |
| **Hybrid (chosen)** | ✅ Right tool for job<br>✅ Best performance<br>✅ Future Dask path<br>✅ Full coverage | ⚠️ Two dependencies | ✅ **Optimal** |

**GeoPandas coverage of GDAL utilities**:

- ✅ **80-90% of common operations**: Read/write, reprojection, conversion, spatial filtering
- ✅ **Built-in spatial analysis**: Joins, overlays, buffers (not in GDAL CLI)
- ⚠️ **Limited advanced OGR**: Transactions, topology, direct SQL
- ✅ **Dask integration**: Critical for future scaling (ADR-0019)

**Performance considerations**:

```python
# Fast: pyogrio for metadata (no DataFrame overhead)
info = pyogrio.read_info(uri)  # Milliseconds

# Efficient: geopandas for processing (when DataFrame is needed)
gdf = gpd.read_file(uri)
gdf_reprojected = gdf.to_crs("EPSG:3857")  # In-memory, vectorized

# Future: Dask for large datasets (partitioned processing)
dgdf = dask_geopandas.read_file(uri, npartitions=8)
dgdf_buffered = dgdf.buffer(100)  # Parallel
```

## Consequences

**Positive**:
- ✅ Optimal performance for metadata operations (pyogrio)
- ✅ Rich DataFrame API for processing (geopandas)
- ✅ Clear path to parallel processing (Dask - ADR-0019)
- ✅ Full GDAL coverage via hybrid approach
- ✅ Pydantic serialization works with both (GeoJSON, WKT)

**Negative**:
- ⚠️ Two dependencies for vector operations (~60MB total)
- ⚠️ Developer must choose right tool (documented in code comments)
- ⚠️ Conversion cost when mixing (pyogrio → geopandas)

**Neutral**:
- Tools will clearly document which backend they use
- ADR-0019 will address parallel processing strategy

## Implementation

**Dependencies** (pyproject.toml):
```toml
dependencies = [
    # Existing
    "pyogrio>=0.7",         # Lightweight metadata, fallback to fiona
    # Add for processing
    "geopandas>=0.14",      # DataFrame-based vector processing
]

[project.optional-dependencies]
dev = [
    # Existing dev deps...
    "dask-geopandas>=0.3",  # For future parallel processing experiments
]
```

**Tool categorization**:

| Tool | Backend | Rationale |
|------|---------|-----------|
| `vector.info` | pyogrio | Metadata only, no processing |
| `vector.reproject` | geopandas | `.to_crs()` is cleaner than manual warp |
| `vector.convert` | geopandas | `.to_file()` handles all formats |
| `vector.spatial_join` | geopandas | Built-in `sjoin()` |
| `vector.buffer` | geopandas | Built-in `.buffer()` |
| Future: `vector.process_large` | dask-geopandas | Parallel processing (ADR-0019) |

## Related

- **ADR-0017**: Python-native over CLI - Establishes Python-first approach
- **ADR-0019**: Parallel processing strategy - Dask integration for scaling
- **ADR-0012**: Resource references - Applies to vector outputs

## References

- [GeoPandas Documentation](https://geopandas.org)
- [pyogrio Documentation](https://pyogrio.readthedocs.io)
- [Dask-GeoPandas](https://dask-geopandas.readthedocs.io)
