from __future__ import annotations

from typing import Any

import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError


def extract_raster_info(
    path: str,
    band: int | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Extract raster metadata using Rasterio.

    Returns a plain dict suitable for constructing the Raster Info model
    or direct JSON serialization from a Resource.
    """
    try:
        with rasterio.Env():
            with rasterio.open(path) as ds:
                if band is not None:
                    if band < 1 or band > ds.count:
                        raise ToolError(
                            f"Band index {band} is out of range. Valid range: 1 to {ds.count}. "
                            f"This raster has {ds.count} band(s)."
                        )
                    ov_levels = ds.overviews(band)
                else:
                    ov_levels = ds.overviews(1) if ds.count >= 1 else []

                crs_str = str(ds.crs) if ds.crs else None
                transform = [
                    ds.transform.a,
                    ds.transform.b,
                    ds.transform.c,
                    ds.transform.d,
                    ds.transform.e,
                    ds.transform.f,
                ]
                dtype_str = ds.dtypes[0] if ds.dtypes else None

                return {
                    "path": path,
                    "driver": ds.driver,
                    "crs": crs_str,
                    "width": ds.width,
                    "height": ds.height,
                    "count": ds.count,
                    "dtype": dtype_str,
                    "transform": transform,
                    "nodata": ds.nodata,
                    "overview_levels": ov_levels,
                    "tags": ds.tags() or {},
                }
    except rasterio.errors.RasterioIOError as e:
        msg = (
            f"Cannot open raster at '{path}'. "
            "Please ensure the file exists and is a valid raster format."
        )
        raise ToolError(msg) from e
    except Exception as e:
        raise ToolError(f"Unexpected error while reading raster metadata: {str(e)}") from e
