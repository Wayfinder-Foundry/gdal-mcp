"""Band-level metadata extraction for raster datasets."""

from __future__ import annotations

from typing import Any

import rasterio
from fastmcp.exceptions import ToolError


def band_metadata(path: str, *, include_statistics: bool = False) -> dict[str, Any]:
    """Return metadata for each band in a raster dataset.

    Args:
        path: Raster dataset path.
        include_statistics: Whether to compute approximate statistics per band.

    Returns:
        Dictionary with path and band metadata list.

    Raises:
        ToolError: If raster cannot be opened.
    """
    bands: list[dict[str, Any]] = []

    try:
        with rasterio.Env():
            with rasterio.open(path) as src:
                for index in range(1, src.count + 1):
                    description = src.descriptions[index - 1] or None
                    dtype = src.dtypes[index - 1] if src.dtypes else None
                    nodata = None
                    if src.nodatavals:
                        nodata = src.nodatavals[index - 1]
                    color_interp = None
                    if src.colorinterp:
                        color_interp = src.colorinterp[index - 1].name

                    band_info: dict[str, Any] = {
                        "band": index,
                        "description": description,
                        "dtype": dtype,
                        "nodata": nodata,
                        "color_interpretation": color_interp,
                    }

                    if include_statistics:
                        try:
                            stats = src.statistics(index, approx=True)
                            band_info["statistics"] = {
                                "min": stats.min,
                                "max": stats.max,
                                "mean": stats.mean,
                                "std": stats.std,
                            }
                        except Exception:
                            # Skip statistics if unavailable
                            band_info["statistics"] = None

                    bands.append(band_info)

        return {"path": path, "band_count": len(bands), "bands": bands}
    except rasterio.errors.RasterioIOError as exc:
        raise ToolError(
            f"Cannot open raster at '{path}'. Ensure the file exists and is a valid raster format."
        ) from exc
