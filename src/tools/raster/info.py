"""Raster info tool using Python-native Rasterio."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.config import resolve_path
from src.models.raster.info import Info
from src.shared.raster.info import extract_raster_info


async def _info(
    uri: str,
    band: int | None = None,
    ctx: Context | None = None,
) -> Info:
    """Return structured metadata for a raster dataset using shared extractor."""
    # Resolve path to absolute
    uri_path = str(resolve_path(uri))

    if ctx:
        await ctx.info(f"[raster_info] Loading metadata for {uri_path}")
    data = extract_raster_info(uri_path, band, ctx)
    if ctx:
        await ctx.info("[raster_info] Metadata extraction complete")
    return Info(
        path=data["path"],
        driver=data.get("driver"),
        crs=data.get("crs"),
        width=int(data["width"]),
        height=int(data["height"]),
        count=int(data["count"]),
        dtype=data.get("dtype"),
        transform=list(data["transform"]),
        bounds=tuple(data["bounds"]),
        nodata=data.get("nodata"),
        overview_levels=list(data.get("overview_levels", [])),
        tags=dict(data.get("tags", {})),
    )


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
