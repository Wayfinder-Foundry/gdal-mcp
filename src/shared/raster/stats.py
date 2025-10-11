from __future__ import annotations

from typing import Any

import numpy as np
import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError
from rasterio.warp import transform_bounds

# Standard percentile values
PERCENTILE_25 = 25.0
PERCENTILE_75 = 75.0
# Extended percentiles for Phase 2B
DEFAULT_PERCENTILES = [10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 99.0]


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

    params keys supported:
    - bands (list[int] | None): Band indices to analyze
    - include_histogram (bool): Include histogram data
    - histogram_bins (int): Number of histogram bins (default: 256)
    - percentiles (list[float]): Custom percentiles (default: extended set)
    - sample_size (int | None): Sample size for large rasters
    - include_extent (bool): Include spatial extent (default: True)
    """
    if params is None:
        params = {}

    bands = params.get("bands")
    include_histogram = bool(params.get("include_histogram", False))
    histogram_bins = int(params.get("histogram_bins", 256))
    percentiles = params.get("percentiles", DEFAULT_PERCENTILES)
    sample_size = params.get("sample_size")
    include_extent = bool(params.get("include_extent", True))

    try:
        with rasterio.Env():
            with rasterio.open(path) as src:
                if bands is None:
                    band_indices = list(range(1, src.count + 1))
                else:
                    band_indices = list(bands)
                    for idx in band_indices:
                        if idx < 1 or idx > src.count:
                            raise ToolError(
                                f"Band index {idx} is out of range. Valid range: 1 to {src.count}."
                            )

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

                    # Sampling for performance
                    if sample_size and valid_count > sample_size:
                        rng = np.random.default_rng(42)
                        sampled_indices = rng.choice(valid_count, size=sample_size, replace=False)
                        valid_data = valid_data[sampled_indices]

                    if valid_count > 0:
                        min_val = float(np.min(valid_data))
                        max_val = float(np.max(valid_data))
                        mean_val = float(np.mean(valid_data))
                        std_val = float(np.std(valid_data))
                        perc_vals = np.percentile(valid_data, percentiles)
                        perc_map = {
                            float(p): float(v) for p, v in zip(percentiles, perc_vals, strict=False)
                        }
                        median_val = float(perc_map.get(50.0, np.median(valid_data)))
                        # Legacy percentiles for backward compatibility
                        p25_val = (
                            float(perc_map.get(PERCENTILE_25))
                            if PERCENTILE_25 in perc_map
                            else None
                        )
                        p75_val = (
                            float(perc_map.get(PERCENTILE_75))
                            if PERCENTILE_75 in perc_map
                            else None
                        )
                    else:
                        min_val = max_val = mean_val = std_val = median_val = None
                        p25_val = p75_val = None
                        perc_map = {}

                    histogram_list: list[dict[str, Any]] = []
                    if include_histogram and valid_count > 0:
                        counts, edges = np.histogram(valid_data, bins=histogram_bins)
                        for i, count in enumerate(counts):
                            histogram_list.append(
                                {
                                    "min_value": float(edges[i]),
                                    "max_value": float(edges[i + 1]),
                                    "count": int(count),
                                }
                            )

                    band_stats_list.append(
                        {
                            "band": int(band_idx),
                            "min": min_val,
                            "max": max_val,
                            "mean": mean_val,
                            "std": std_val,
                            "median": median_val,
                            "percentile_25": p25_val,  # Legacy field
                            "percentile_75": p75_val,  # Legacy field
                            "percentiles": perc_map,  # All percentiles
                            "valid_count": int(valid_count),
                            "nodata_count": int(nodata_count),
                            "histogram": histogram_list,
                        }
                    )

                # Prepare base response
                result = {
                    "path": path,
                    "band_stats": band_stats_list,
                    "total_pixels": int(total_pixels),
                }

                # Add spatial extent if requested
                if include_extent:
                    bounds = src.bounds
                    crs_str = str(src.crs) if src.crs else None

                    extent_info: dict[str, Any] = {
                        "bounds": {
                            "left": bounds.left,
                            "bottom": bounds.bottom,
                            "right": bounds.right,
                            "top": bounds.top,
                        },
                        "crs": crs_str,
                    }

                    # Add WGS84 bounds for global context if CRS is defined
                    if src.crs:
                        try:
                            wgs84_bounds = transform_bounds(
                                src.crs,
                                "EPSG:4326",
                                bounds.left,
                                bounds.bottom,
                                bounds.right,
                                bounds.top,
                            )
                            extent_info["bounds_wgs84"] = {
                                "west": wgs84_bounds[0],
                                "south": wgs84_bounds[1],
                                "east": wgs84_bounds[2],
                                "north": wgs84_bounds[3],
                            }
                        except Exception:
                            # If reprojection fails, skip WGS84 bounds
                            pass

                    result["spatial_extent"] = extent_info

                return result
    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            f"Cannot open raster at '{path}'. Ensure the file exists and is a valid raster format."
        ) from e
    except MemoryError as e:
        raise ToolError(
            f"Out of memory while computing statistics for '{path}'. Consider using sampling."
        ) from e
    except Exception as e:
        raise ToolError(f"Unexpected error while computing statistics: {str(e)}") from e
