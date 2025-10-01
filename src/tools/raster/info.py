"""Raster info tool using Python-native Rasterio."""
from __future__ import annotations

import rasterio

from src.app import mcp
from src.models.raster import RasterInfo


@mcp.tool(
    name="raster.info",
    description="Inspect a raster dataset and return structured metadata.",
)
async def raster_info(uri: str, band: int | None = None) -> RasterInfo:
    """Return structured metadata for a raster dataset.

    Args:
        uri: Path/URI to the raster dataset (file://, local path, VSI-supported).
        band: Optional band index (1-based) for overview introspection.

    Returns:
        RasterInfo: Structured raster metadata with JSON schema.
    """
    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    with rasterio.Env():
        with rasterio.open(uri) as ds:
            # Validate band if provided
            if band is not None:
                if band < 1 or band > ds.count:
                    raise ValueError(
                        f"Band index out of range: {band} (valid: 1..{ds.count})"
                    )
                ov_levels = ds.overviews(band)
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

            # Build Pydantic model (FastMCP auto-serializes to JSON with schema)
            return RasterInfo(
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
