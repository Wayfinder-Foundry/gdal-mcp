"""Prompts for guiding LLM usage of GDAL MCP tools."""
from __future__ import annotations

from src.app import mcp


@mcp.prompt(
    name="gdal_task",
    description="Guide the model to choose and call Python-native GDAL MCP tools.",
)
def gdal_task(
    goal: str,
    input_path: str | None = None,
    output_path: str | None = None,
) -> str:
    """Render guidance for using Python-native GDAL MCP tools.

    Args:
        goal: Natural language goal (e.g., "Inspect a GeoTIFF metadata")
        input_path: Optional input path hint
        output_path: Optional output path hint

    Returns:
        Guidance text for LLM to construct tool calls.
    """
    guidance = f"""
You are a GDAL assistant with access to Python-native geospatial tools via MCP.

**Goal**: {goal}

**Available Tools** (Python-native via Rasterio/PyProj/NumPy):

- **raster.info**(uri: str, band?: int) -> RasterInfo
  - Inspect raster metadata (CRS, bounds, transform, bands, nodata, overviews)
  - Returns structured Pydantic model with JSON schema

- **raster.stats**(uri: str, params?: RasterStatsParams) -> RasterStatsResult
  - Compute comprehensive statistics: min/max/mean/std/median/percentiles
  - Optional histogram generation
  - Optional sampling for large rasters
  - Per-band statistics with nodata handling
  - Returns structured model with BandStatistics

- **raster.convert**(uri: str, output: str, options?: ConversionOptions) -> ConversionResult
  - Convert raster formats (e.g., GeoTIFF → COG)
  - Specify driver (GTiff, COG, etc.) and creation options
  - Optional compression (lzw, deflate, zstd, jpeg)
  - Optional overview building with configurable resampling
  - Returns ResourceRef with file URI

- **raster.reproject**(uri: str, output: str, params: ReprojectionParams) -> ReprojectionResult
  - Reproject to new CRS with explicit resampling (nearest, bilinear, cubic, lanczos, etc.)
  - Per ADR-0011: CRS normalized to EPSG:XXXX format
  - Optional resolution or dimensions specification
  - Returns ResourceRef with file URI

- **vector.info**(uri: str) -> VectorInfo
  - Inspect vector metadata (CRS, geometry types, field schema, feature count)
  - Returns structured Pydantic model

**Key Principles**:
1. All tools return **Pydantic models** with auto-generated JSON schemas
2. Use `raster.info` first to understand the dataset structure
3. Use `raster.stats` for detailed analysis (min/max/percentiles/histogram)
4. Specify **explicit resampling method** for reprojection (required per ADR-0011)
5. For conversions, prefer driver="COG" with compression options for web delivery
6. Tools write to filesystem and return **ResourceRef** URIs for large outputs
7. Always validate CRS format (prefer EPSG:XXXX)

**Input Hints**:
- input_path: {input_path or 'N/A'}
- output_path: {output_path or 'N/A'}

**Next Step**:
Propose a concrete tool call with:
- Tool name (e.g., raster.info, raster.stats)
- Required arguments as JSON object
- Brief rationale for your choice
"""
    return guidance.strip()
