"""Raster info tool using Python-native Rasterio."""
from __future__ import annotations

import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.models.raster.info import Info


async def _info(
    uri: str, 
    band: int | None = None,
    ctx: Context | None = None,
) -> Info:
    """Core logic: Return structured metadata for a raster dataset.

    Args:
        uri: Path/URI to the raster dataset (file://, local path, VSI-supported).
        band: Optional band index (1-based) for overview introspection.
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Info: Structured raster metadata with JSON schema.
    
    Raises:
        ToolError: If raster cannot be opened or band index is invalid.
    """
    if ctx:
        await ctx.info(f"📂 Opening raster: {uri}")
    
    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    try:
        with rasterio.Env():
            with rasterio.open(uri) as ds:
                if ctx:
                    await ctx.debug(
                        f"✓ Driver: {ds.driver}, Size: {ds.width}x{ds.height}, "
                        f"Bands: {ds.count}, CRS: {ds.crs}"
                    )
                
                # Validate band if provided
                if band is not None:
                    if band < 1 or band > ds.count:
                        raise ToolError(
                            f"Band index {band} is out of range. "
                            f"Valid range: 1 to {ds.count}. "
                            f"This raster has {ds.count} band(s)."
                        )
                    ov_levels = ds.overviews(band)
                    if ctx:
                        await ctx.debug(f"Band {band} overview levels: {ov_levels}")
                else:
                    ov_levels = ds.overviews(1) if ds.count >= 1 else []

                # Normalize CRS to string per ADR-0011
                crs_str = str(ds.crs) if ds.crs else None

                # Affine transform as list[float]
                transform = [
                    ds.transform.a,
                    ds.transform.b,
                    ds.transform.c,
                    ds.transform.d,
                    ds.transform.e,
                    ds.transform.f,
                ]

                # Bounds as tuple
                bounds = (
                    ds.bounds.left,
                    ds.bounds.bottom,
                    ds.bounds.right,
                    ds.bounds.top,
                )

                # First band dtype
                dtype_str = ds.dtypes[0] if ds.dtypes else None

                if ctx:
                    await ctx.info("✓ Metadata extraction complete")

                # Build Pydantic model (FastMCP auto-serializes to JSON with schema)
                return Info(
                    path=uri,
                    driver=ds.driver,
                    crs=crs_str,
                    width=ds.width,
                    height=ds.height,
                    count=ds.count,
                    dtype=dtype_str,
                    transform=transform,
                    bounds=bounds,
                    nodata=ds.nodata,
                    overview_levels=ov_levels,
                    tags=ds.tags() or {},
                )
    
    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            f"Cannot open raster at '{uri}'. "
            f"Please ensure: (1) file exists, (2) file is a valid raster format. "
            f"Supported formats: GeoTIFF (.tif), COG, PNG (.png), JPEG (.jpg), "
            f"NetCDF (.nc), HDF5 (.h5), and other GDAL-supported formats. "
            f"Original error: {str(e)}"
        ) from e
    except Exception as e:
        raise ToolError(
            f"Unexpected error while reading raster metadata: {str(e)}"
        ) from e


@mcp.tool(
    name="raster_info",
    description=(
        "Inspect raster metadata using Python-native Rasterio. "
        "USE WHEN: Need to understand raster properties before processing, "
        "verify CRS and spatial extent, check band count and data types, "
        "inspect nodata values, or examine overview levels for multi-resolution data. "
        "REQUIRES: uri (path or URI to raster file, supports file://, /vsi paths). "
        "OPTIONAL: band (1-based band index for overview introspection). "
        "OUTPUT: RasterInfo with driver (e.g. 'GTiff'), CRS (e.g. 'EPSG:4326'), "
        "width/height (pixels), count (number of bands), dtype (e.g. 'uint8'), "
        "transform (6-element affine: [a, b, c, d, e, f]), "
        "bounds (minx, miny, maxx, maxy), nodata value, overview_levels (list), "
        "and tags (metadata dict). "
        "SIDE EFFECTS: None (read-only operation, no file modification)."
    ),
)
async def info(
    uri: str, 
    band: int | None = None, 
    ctx: Context | None = None,
) -> Info:
    """MCP tool wrapper for raster info."""
    return await _info(uri, band, ctx)
