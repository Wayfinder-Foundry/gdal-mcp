# GDAL MCP Tools Reference

Complete reference for all available tools in GDAL MCP.

---

## Tool Categories

- [Raster Tools](#raster-tools) - Raster data operations (info, convert, reproject, stats)
- [Vector Tools](#vector-tools) - Vector data operations (info, reproject, convert, clip, buffer, simplify)
- [Reflection Tools](#reflection-tools) - Epistemic justification system

---

## Raster Tools

### `raster_info`

**Purpose:** Inspect raster metadata without reading pixel data.

**Use cases:** 
- Understand projection, resolution, extent before processing
- Verify CRS and data type
- Check for overviews and compression

**Parameters:**
- `uri` (required): Path to raster file

**Returns:**
- Driver name (e.g., "GTiff")
- CRS (e.g., "EPSG:4326")
- Bounds (minx, miny, maxx, maxy)
- Transform (6-element affine)
- Width/height (pixels)
- Band count and data types
- Nodata value
- Overview levels (if present)

**Example conversation:**
```
User: "What's the CRS and resolution of elevation.tif?"
AI: *calls raster_info*
    "The DEM is in EPSG:4326 (WGS84) with 0.000277° resolution (~30m at equator).
     It covers bounds: [-122.5, 37.5, -122.0, 38.0]"
```

---

### `raster_convert`

**Purpose:** Format conversion with compression and multi-resolution overviews.

**Use cases:**
- Create Cloud-Optimized GeoTIFFs (COG)
- Reduce file size with compression
- Build pyramids (overviews) for fast rendering
- Migrate between formats

**Parameters:**
- `uri` (required): Path to source raster
- `output` (required): Path for output file
- `driver` (optional): Output format
  - `GTiff` - Standard GeoTIFF
  - `COG` - Cloud-Optimized GeoTIFF (recommended for web)
  - `PNG` - Portable Network Graphics
  - `JPEG` - JPEG (lossy, for imagery)
- `compression` (optional): Compression algorithm
  - `deflate` - Lossless, good ratio (recommended)
  - `lzw` - Lossless, compatible
  - `zstd` - Best compression, newer format
  - `jpeg` - Lossy, for imagery
  - `none` - No compression
- `tiled` (optional, default: True): Create tiled output (256×256 blocks)
- `overviews` (optional): List of overview levels (e.g., [2, 4, 8, 16])

**Returns:**
- ResourceRef (output file URI, path, size, metadata)
- Driver name
- Compression method used
- Size in bytes
- Overviews built (if requested)

**Example conversation:**
```
User: "Optimize this 5GB satellite image for web serving"
AI: "Converting to COG with DEFLATE compression and overviews..."
    *calls raster_convert with driver=COG, compression=deflate, overviews=[2,4,8,16]*
    "Done! Reduced to 1.2GB (76% savings). Ready for cloud storage."
```

---

### `raster_reproject` ⚡

**Purpose:** Reproject to new coordinate system with methodological justification.

**🧠 Reflection Required:**
- **CRS selection** - Why this projection? What properties must be preserved?
- **Resampling method** - How to interpolate? What artifacts are acceptable?

**Use cases:**
- Transform to analysis-appropriate CRS
- Align multiple datasets to common projection
- Prepare for web mapping
- Fix incorrect projections

**Required parameters:**
- `uri`: Path to source raster
- `output`: Path for output file
- `dst_crs`: Target projection (e.g., "EPSG:32610" for UTM Zone 10N)
- `resampling`: Interpolation method
  - `nearest` - Categorical data (land cover, classifications)
  - `bilinear` - Fast, good for continuous data
  - `cubic` - Smoothest, best for DEMs and visualization
  - `lanczos` - Highest quality, slower

**Optional parameters:**
- `src_crs`: Override source CRS if missing/incorrect
- `resolution`: Target pixel size [x, y] in destination units
- `bounds`: Crop to area [left, bottom, right, top]
- `width`/`height`: Explicit output dimensions in pixels
- `nodata`: Override nodata value

**Returns:**
- ResourceRef (output file)
- Source CRS
- Destination CRS
- Resampling method used
- Output transform, width, height
- Bounds in destination CRS

**Reflection behavior:**
1. First use: AI prompted to justify CRS choice and resampling method
2. Justifications cached based on domain (crs_datum, resampling)
3. Future operations with same CRS/resampling: instant (cache hit)
4. **Cross-domain:** CRS justification works for both raster and vector!

**Example conversation:**
```
User: "Reproject this land cover map to UTM for area calculations"
AI: *raster_info shows categorical data*
    *reflection: Why UTM? → accurate area/distance in local zone*
    *reflection: Why nearest? → preserves exact class values, no new categories*
    "Reprojecting to EPSG:32610 with nearest-neighbor..."
    *executes with justified methodology*
```

---

### `raster_stats`

**Purpose:** Compute statistical summaries and histograms.

**Use cases:**
- Understand data distribution
- Find outliers or invalid values
- Validate processing results
- Generate metadata for visualization

**Parameters:**
- `uri` (required): Path to raster file
- `bands` (optional): List of band indices (1-based), default: all bands
- `include_histogram` (optional, default: False): Generate histogram
- `histogram_bins` (optional, default: 256): Number of histogram bins (2-1024)
- `percentiles` (optional): List of percentiles to compute (e.g., [25, 50, 75])
- `sample_size` (optional): Sample random pixels instead of reading all (for large rasters)

**Returns:**
- Total pixel count
- Per-band statistics:
  - min, max, mean, std
  - median
  - Percentiles (if requested)
  - Valid pixel count
  - Nodata pixel count
  - Histogram bins (if requested)

**Example conversation:**
```
User: "Check the elevation range in this DEM"
AI: *calls raster_stats*
    "Elevation ranges from 145m to 2,847m with mean 892m.
     Distribution shows two peaks (bimodal) - likely valley and ridge areas."
```

---

## Vector Tools

### `vector_info`

**Purpose:** Inspect vector dataset metadata.

**Use cases:**
- Understand vector structure before processing
- Verify CRS and spatial extent
- Check geometry types and attribute fields
- Validate feature count

**Parameters:**
- `uri` (required): Path to vector dataset

**Returns:**
- Driver name (e.g., "ESRI Shapefile", "GeoJSON", "GPKG")
- CRS (e.g., "EPSG:4326")
- Layer count
- Geometry types (e.g., ["Point", "MultiPolygon"])
- Feature count
- Field schema (name, type pairs)
- Bounds (minx, miny, maxx, maxy)

**Supported formats:** Shapefile, GeoPackage, GeoJSON, KML, GML, and other OGR formats

**Example conversation:**
```
User: "What's in this shapefile?"
AI: *calls vector_info*
    "It's a polygon layer with 1,247 parcels in EPSG:2227 (California State Plane).
     Fields: parcel_id (string), area_sqft (float), zoning (string), assessed_value (int)"
```

---

### `vector_reproject` ⚡

**Purpose:** Reproject vector dataset to new CRS.

**🧠 Reflection Required:**
- **CRS selection** - Same reflection as `raster_reproject` (cross-domain cache sharing!)

**Use cases:**
- Convert lat/lon to Web Mercator for web maps
- Transform to local UTM for accurate measurements
- Align datasets to common projection
- Fix incorrect/missing CRS

**Required parameters:**
- `uri`: Path to source vector
- `output`: Path for output file
- `dst_crs`: Target projection (e.g., "EPSG:3857", "EPSG:4326")

**Optional parameters:**
- `src_crs`: Override source CRS if missing/incorrect

**Returns:**
- ResourceRef (output file)
- Source CRS
- Destination CRS
- Feature count
- Geometry type
- Bounds in destination CRS

**Reflection behavior:**
- Shares CRS reflection cache with `raster_reproject`
- If you've justified EPSG:3857 for raster, no re-prompting for vector!

**Example conversation:**
```
User: "Reproject this GeoJSON to Web Mercator for my web map"
AI: [If already justified EPSG:3857 for raster earlier]
    *cache hit - no reflection needed*
    "Reprojecting to EPSG:3857 using cached justification..."
    *instant execution*
```

---

### `vector_convert`

**Purpose:** Convert between vector formats with encoding control.

**Use cases:**
- Migrate Shapefile → GeoPackage (single file, no limits)
- Convert GeoJSON → Shapefile (desktop GIS compatibility)
- Fix encoding issues (e.g., non-UTF-8 Shapefiles)
- Prepare data for specific software

**Parameters:**
- `uri` (required): Path to source vector
- `output` (required): Path for output file (extension determines format)
- `driver` (optional): Target format (auto-detected from extension)
  - `.shp` → ESRI Shapefile
  - `.gpkg` → GeoPackage
  - `.geojson` → GeoJSON
  - `.kml` → KML
  - `.gml` → GML
- `encoding` (optional, default: "UTF-8"): Character encoding
  - `UTF-8` - Modern standard (recommended)
  - `ISO-8859-1` - Legacy compatibility

**Returns:**
- ResourceRef (output file)
- Source driver
- Destination driver
- Feature count
- Geometry type
- Encoding used

**Why GeoPackage?**
- Single file (no .shp/.shx/.dbf/.prj mess)
- UTF-8 native (no encoding issues)
- No field name limits (Shapefile has 10 char limit)
- Efficient spatial indexing
- Modern standard

**Example conversation:**
```
User: "Convert this Shapefile to GeoPackage"
AI: *calls vector_convert(uri="parcels.shp", output="parcels.gpkg")*
    "Converted 1,247 features from ESRI Shapefile to GeoPackage with UTF-8 encoding.
     Output: parcels.gpkg (single file, 2.4 MB)"
```

---

### `vector_clip`

**Purpose:** Spatial subsetting by bounding box or mask geometry.

**Use cases:**
- Extract features within study area
- Crop to area of interest
- Reduce dataset size
- Prepare data for focused analysis

**Parameters:**
- `uri` (required): Path to source vector
- `output` (required): Path for output file
- `bounds` (optional): Bounding box [minx, miny, maxx, maxy]
- `mask` (optional): Path to mask geometry file

**Returns:**
- ResourceRef (output file)
- Input feature count
- Output feature count (after clipping)
- Clip method used (bbox or mask)
- Bounds of clipped output

**Example conversation:**
```
User: "Extract parcels within this bounding box: [-122.5, 37.5, -122.4, 37.6]"
AI: *calls vector_clip with bounds*
    "Clipped to 847 features (from 1,247 original).
     Output covers bbox: [-122.5, 37.5, -122.4, 37.6]"
```

---

### `vector_buffer`

**Purpose:** Proximity analysis with configurable resolution.

**Use cases:**
- Create buffer zones around features
- Riparian zone analysis (buffer around streams)
- Service area analysis (buffer around facilities)
- Impact zone modeling

**Parameters:**
- `uri` (required): Path to source vector
- `output` (required): Path for output file
- `distance` (required): Buffer distance in layer units
- `resolution` (optional, default: 16): Segments per quadrant (quality vs performance)

**Returns:**
- ResourceRef (output file)
- Buffer distance used
- Resolution (segments per quadrant)
- Feature count
- Output bounds

**Example conversation:**
```
User: "Create 100m buffer zones around these stream segments"
AI: *calls vector_buffer(distance=100)*
    "Created buffer zones: 100m radius, 16 segments per quadrant.
     Output: 342 buffered polygons"
```

---

### `vector_simplify`

**Purpose:** Geometry simplification for performance and file size reduction.

**Use cases:**
- Reduce vertex count for web mapping
- Decrease file size
- Improve rendering performance
- Generalize detail level

**Parameters:**
- `uri` (required): Path to source vector
- `output` (required): Path for output file
- `tolerance` (required): Simplification tolerance in layer units
- `algorithm` (optional, default: "douglas-peucker"): Simplification algorithm
  - `douglas-peucker` - Classic line simplification
  - `visvalingam` - Area-based simplification

**Returns:**
- ResourceRef (output file)
- Algorithm used
- Tolerance value
- Feature count
- Vertex count reduction stats

**Example conversation:**
```
User: "Simplify this high-resolution coastline for web display"
AI: *calls vector_simplify(tolerance=100, algorithm="douglas-peucker")*
    "Simplified 1,847 features using Douglas-Peucker (tolerance=100m).
     Reduced vertices by 78% (1.2M → 270K). File size: 18MB → 4MB"
```

---

## Reflection Tools

### `store_justification`

**Purpose:** Explicitly cache epistemic justifications (usually called automatically).

**Use cases:**
- Manual workflow documentation
- Pre-emptive justification caching
- Custom reflection workflows

**Parameters:**
- `tool_name`: Name of tool this justification is for
- `domain`: Reflection domain (crs_datum, resampling, hydrology, aggregation)
- `prompt_name`: Name of the prompt that generated this
- `prompt_args`: Arguments used in the prompt (dict)
- `justification`: The structured justification (dict with intent, alternatives, choice, confidence)

**Returns:**
- Confirmation message with cache key

**Note:** This tool is primarily used internally by the reflection system. You typically won't call it directly.

---

## Reflection System Overview

### What is Reflection?

**Reflection** is the epistemic middleware system that requires AI agents to **justify methodological decisions** before executing operations with geospatial consequences.

### Why Reflection Matters

Geospatial operations aren't just technical commands - they're **scientific methodological choices**:
- Choosing a CRS affects accuracy (conformal vs equal-area vs equidistant)
- Choosing resampling affects data quality (artifacts, value preservation)
- These choices have real consequences for analysis results

### How It Works

1. **Tool with reflection requirement** (e.g., `raster_reproject`)
2. **Middleware intercepts** the call
3. **Cache check**: Has this methodology been justified before?
   - **Yes** → Instant execution (cache hit)
   - **No** → Prompt AI for justification
4. **AI provides structured reasoning:**
   - Intent (what property to preserve?)
   - Alternatives considered (what else was possible?)
   - Choice rationale (why this method?)
   - Tradeoffs acknowledged (what are the limitations?)
   - Confidence level (high/medium/low)
5. **Justification cached** for future use
6. **Operation proceeds** with validated methodology

### Reflection Domains

- **`crs_datum`** - Coordinate system selection
  - Cache key: `dst_crs` only
  - **Cross-domain**: Works for both raster and vector!
- **`resampling`** - Interpolation method choice
  - Cache key: `method` only
- **`hydrology`** - DEM conditioning (planned)
- **`aggregation`** - Statistical methods (planned)

### Cross-Domain Cache Sharing

**The Innovation:** Methodological reasoning transcends data types.

A CRS justification for EPSG:3857 is about the projection's properties (conformal, web-optimized, distortion tradeoffs), **not whether you're working with raster or vector data**.

**Example workflow:**
```
1. raster_reproject(dst_crs="EPSG:3857") → Justification prompted and cached
2. vector_reproject(dst_crs="EPSG:3857") → Cache hit! No re-prompting needed
3. Result: 75% cache hit rate in multi-operation workflows
```

### Cache Behavior

**Cache structure:**
```
.preflight/justifications/
├── crs_datum/
│   └── sha256:{hash}.json
└── resampling/
    └── sha256:{hash}.json
```

**Cache keys are based on:**
- Domain (e.g., crs_datum)
- Prompt hash (ensures prompt hasn't changed)
- Prompt arguments (e.g., dst_crs="EPSG:3857")

**NOT based on tool name** - this enables cross-domain sharing!

### Reflection Philosophy

**Goal:** Preserve agent autonomy while amplifying expertise.

The reflection system:
- ✅ Requires justification for methodological choices
- ✅ Educates through structured reasoning
- ✅ Caches efficiently (75%+ hit rates)
- ✅ Enables cross-domain knowledge transfer
- ✅ Creates audit trail for reproducibility
- ❌ Does NOT block operations arbitrarily
- ❌ Does NOT prescribe specific methods
- ❌ Does NOT repeat prompts unnecessarily

**It's conversational guidance, not gatekeeping.**

---

## Related Documentation

- [README.md](README.md) - Project overview and philosophy
- [QUICKSTART.md](QUICKSTART.md) - Installation and setup
- [CHANGELOG.md](CHANGELOG.md) - Release history
- [docs/VISION.md](docs/VISION.md) - Long-term roadmap
- [docs/ADR/](docs/ADR/) - Architecture decisions
