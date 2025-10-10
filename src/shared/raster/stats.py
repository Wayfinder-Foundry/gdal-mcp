from __future__ import annotations

from typing import Any

import numpy as np
import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError


def stats(
    path: str,
    params: dict[str, Any] | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Compute raster statistics; returns plain dict for resource/tool consumption.

    params keys supported: bands (list[int] | None), include_histogram (bool),
    histogram_bins (int), percentiles (list[float]), sample_size (int | None).
    """
    if params is None:
        params = {}

    bands = params.get("bands")
    include_histogram = bool(params.get("include_histogram", False))
    histogram_bins = int(params.get("histogram_bins", 256))
    percentiles = params.get("percentiles", [25.0, 50.0, 75.0])
    sample_size = params.get("sample_size")

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
                        p25_val = float(perc_map.get(25.0)) if 25.0 in perc_map else None
                        p75_val = float(perc_map.get(75.0)) if 75.0 in perc_map else None
                    else:
                        min_val = max_val = mean_val = std_val = median_val = None
                        p25_val = p75_val = None

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
                            "percentile_25": p25_val,
                            "percentile_75": p75_val,
                            "valid_count": int(valid_count),
                            "nodata_count": int(nodata_count),
                            "histogram": histogram_list,
                        }
                    )

                return {
                    "path": path,
                    "band_stats": band_stats_list,
                    "total_pixels": int(total_pixels),
                }
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
