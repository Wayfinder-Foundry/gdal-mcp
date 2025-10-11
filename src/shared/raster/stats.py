"""Raster statistics helpers with extended metadata support."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import rasterio
from fastmcp.exceptions import ToolError
from rasterio.crs import CRS
from rasterio.io import DatasetReader
from rasterio.warp import transform_bounds

from src.shared.enum import Percentile, direction

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from fastmcp import Context
else:  # pragma: no cover - runtime fallback when typing is unavailable
    Context = Any

LOGGER = logging.getLogger(__name__)
RANDOM_SEED = 42  # For reproducible sampling
BINS_8BIT = 256
EPSG_WGS84 = 4326


def _compute_band_statistics(
    valid_data: np.ndarray,
    percentiles: list[float] | tuple[float, ...],
    sample_size: int | None,
) -> dict[str, Any]:
    """Compute statistics for a single band.

    Args:
        valid_data: Array of valid (non-nodata) pixel values
        percentiles: List of percentile values to compute
        sample_size: Optional sample size for large datasets

    Returns:
        Dictionary with min, max, mean, std, median, percentiles
    """
    valid_count = len(valid_data)

    # Sample for performance if needed
    if sample_size and valid_count > sample_size:
        rng = np.random.default_rng(RANDOM_SEED)
        sampled_indices = rng.choice(valid_count, size=sample_size, replace=False)
        valid_data = valid_data[sampled_indices]

    if valid_count == 0:
        return {
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "median": None,
            "percentile_25": None,
            "percentile_75": None,
            "percentiles": {},
        }

    min_val = float(np.min(valid_data))
    max_val = float(np.max(valid_data))
    mean_val = float(np.mean(valid_data))
    std_val = float(np.std(valid_data))

    perc_vals = np.percentile(valid_data, percentiles)
    perc_map = {float(p): float(v) for p, v in zip(percentiles, perc_vals, strict=False)}

    median_val = float(perc_map.get(Percentile.P50, np.median(valid_data)))

    # Legacy percentiles for backward compatibility
    p25_key = float(Percentile.P25)
    p75_key = float(Percentile.P75)
    p25_val = float(perc_map.get(p25_key)) if p25_key in perc_map else None
    p75_val = float(perc_map.get(p75_key)) if p75_key in perc_map else None

    return {
        "min": min_val,
        "max": max_val,
        "mean": mean_val,
        "std": std_val,
        "median": median_val,
        "percentile_25": p25_val,
        "percentile_75": p75_val,
        "percentiles": perc_map,
    }


def _build_histogram(valid_data: np.ndarray, bins: int) -> list[dict[str, Any]]:
    """Build histogram data for valid pixel values.

    Args:
        valid_data: Array of valid pixel values
        bins: Number of histogram bins

    Returns:
        List of histogram bin dictionaries
    """
    if len(valid_data) == 0:
        return []

    counts, edges = np.histogram(valid_data, bins=bins)
    histogram_list = []
    for i, count in enumerate(counts):
        histogram_list.append(
            {
                "min_value": float(edges[i]),
                "max_value": float(edges[i + 1]),
                "count": int(count),
            },
        )
    return histogram_list


def _compute_spatial_extent(src: DatasetReader) -> dict[str, Any]:
    """Compute spatial extent with native CRS and WGS84 bounds.

    Args:
        src: Open rasterio dataset

    Returns:
        Dictionary with bounds in native CRS and optionally WGS84
    """
    bounds = src.bounds
    crs_str = str(src.crs) if src.crs else None

    extent_info: dict[str, Any] = {
        "bounds": {
            direction.Relative.LEFT: bounds.left,
            direction.Relative.BOTTOM: bounds.bottom,
            direction.Relative.RIGHT: bounds.right,
            direction.Relative.TOP: bounds.top,
        },
        "crs": crs_str,
    }

    # Add WGS84 bounds for global context if CRS is defined
    if src.crs:
        try:
            west, south, east, north = transform_bounds(
                src.crs,
                CRS.from_epsg(EPSG_WGS84),
                bounds.left,
                bounds.bottom,
                bounds.right,
                bounds.top,
            )
            extent_info["bounds_wgs84"] = {
                direction.Cardinal.WEST: west,
                direction.Cardinal.SOUTH: south,
                direction.Cardinal.EAST: east,
                direction.Cardinal.NORTH: north,
            }
        except (rasterio.errors.CRSError, ValueError) as exc:  # type: ignore[attr-defined]
            LOGGER.warning(
                "Failed to compute WGS84 bounds for dataset with CRS %s: %s",
                src.crs,
                exc,
            )

    return extent_info


def stats(
    path: str,
    params: dict[str, Any] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Compute raster statistics with extended percentiles and spatial extent.

    Phase 2B enhancements:
    - Default percentiles: 10th, 25th, 50th, 75th, 90th, 95th, 99th
    - Spatial extent with bounds in native CRS and WGS84
    - Enhanced metadata for AI decision-making

    Args:
        path: Path to raster file
        params: Optional parameters dictionary with keys:
            - bands (list[int] | None): Band indices to analyze
            - include_histogram (bool): Include histogram data
            - histogram_bins (int): Number of histogram bins
            - percentiles (list[float]): Custom percentiles
            - sample_size (int | None): Sample size for large rasters
            - include_extent (bool): Include spatial extent
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary with path, band_stats, total_pixels, and optional spatial_extent
    """
    if params is None:
        params = {}

    bands = params.get("bands")
    include_histogram = bool(params.get("include_histogram", False))
    histogram_bins = int(params.get("histogram_bins", BINS_8BIT))
    percentiles = params.get("percentiles", Percentile.all())
    sample_size = params.get("sample_size")
    include_extent = bool(params.get("include_extent", True))

    result: dict[str, Any] | None = None

    try:
        with rasterio.Env(), rasterio.open(path) as src:
            if bands is None:
                band_indices = list(range(1, src.count + 1))
            else:
                band_indices = list(bands)
                for idx in band_indices:
                    if idx < 1 or idx > src.count:
                        message = (
                            f"Band index {idx} is out of range. Valid range: 1 to {src.count}."
                        )
                        raise ToolError(message)

            total_pixels = src.width * src.height
            band_stats_list: list[dict[str, Any]] = []

            for band_idx in band_indices:
                if src.nodata is not None:
                    data = src.read(band_idx, masked=True)
                    valid_data = data.compressed()
                    valid_count = int(valid_data.size)
                    nodata_count = int(total_pixels - valid_count)
                else:
                    data = src.read(band_idx)
                    valid_data = data.ravel()
                    valid_count = int(valid_data.size)
                    nodata_count = 0

                # Compute statistics
                band_stats = _compute_band_statistics(valid_data, percentiles, sample_size)

                # Build histogram if requested
                histogram_list = (
                    _build_histogram(valid_data, histogram_bins) if include_histogram else []
                )

                band_stats_list.append(
                    {
                        "band": int(band_idx),
                        **band_stats,
                        "valid_count": int(valid_count),
                        "nodata_count": int(nodata_count),
                        "histogram": histogram_list,
                    },
                )
            # Prepare base response after processing all bands
            result = {
                "path": path,
                "band_stats": band_stats_list,
                "total_pixels": int(total_pixels),
            }

            # Add spatial extent if requested
            if include_extent:
                result["spatial_extent"] = _compute_spatial_extent(src)
    except rasterio.errors.RasterioIOError as e:
        message = (
            f"Cannot open raster at '{path}'. Ensure the file exists and is a valid raster format."
        )
        raise ToolError(message) from e
    except MemoryError as e:
        message = f"Out of memory while computing statistics for '{path}'. Consider using sampling."
        raise ToolError(message) from e
    except Exception as e:
        message = f"Unexpected error while computing statistics: {e!s}"
        raise ToolError(message) from e

    if result is None:
        raise ToolError("Failed to compute statistics for unknown reasons.")

    return result
