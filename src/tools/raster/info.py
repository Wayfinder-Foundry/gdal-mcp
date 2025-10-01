from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional

import rasterio

from gdal_mcp.app import mcp
from gdal_mcp.models import RasterInfo


@mcp.tool(name="raster.info", description="Inspect a raster dataset and return structured metadata.")
async def raster_info(uri: str, band: Optional[int] = None) -> Dict[str, Any]:
    """Return structured metadata for a raster dataset.

    Args:
        uri: Path/URI to the raster dataset (file://, local path, VSI-supported uri).
        band: Optional band index (1-based) for overview introspection.

    Returns:
        A dict containing:
          - info: RasterInfo (as dict) with core metadata
          - text: brief human-readable summary
    """
    # Open with rasterio; callers should supply accessible URIs
    with rasterio.Env():
        with rasterio.open(uri) as ds:
            # Validate band if provided
            if band is not None:
                if band < 1 or band > ds.count:
                    raise ValueError(f"Band index out of range: {band} (1..{ds.count})")
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
            bounds = (ds.bounds.left, ds.bounds.bottom, ds.bounds.right, ds.bounds.top)
            dtype0 = ds.dtypes[0] if getattr(ds, "dtypes", None) else None

            info = RasterInfo(
                path=uri,
                driver=ds.driver,
                crs=crs_str,
                width=ds.width,
                height=ds.height,
                count=ds.count,
                dtype=dtype0,
                transform=transform,
                bounds=bounds,
                nodata=ds.nodata,
                overview_levels=ov_levels,
                tags=ds.tags() or {},
            )

    summary = (
        f"{info.driver or 'Raster'} {info.width}x{info.height}x{info.count}"
        + (f" CRS={info.crs}" if info.crs else "")
    )
    return {"info": asdict(info), "text": summary}
