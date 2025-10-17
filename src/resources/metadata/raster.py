"""Metadata resource for raster datasets."""

from __future__ import annotations

from typing import Any

from src.app import mcp
from src.shared import raster


@mcp.resource("metadata://{file}/raster")
def get_raster_metadata(file: str) -> dict[str, Any]:
    """Get raster spatial properties (read-only).

    Returns driver, CRS, bounds, transform, width/height, band count, dtype,
    nodata, overview levels, and tags. Used by AI during planning to
    understand file properties before choosing operations and parameters.
    """
    return raster.info(file)
