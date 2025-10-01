"""Raster statistics tool using Python-native Rasterio + NumPy."""
from __future__ import annotations

import numpy as np
import rasterio

from src.app import mcp
from src.models.raster import RasterStatsParams, RasterStatsResult, BandStatistics, HistogramBin


async def compute_raster_stats(
    uri: str,
    params: RasterStatsParams | None = None,
) -> RasterStatsResult:
    """Core logic: Compute comprehensive statistics for a raster dataset.

    Args:
        uri: Path/URI to the raster dataset.
        params: Statistics parameters (bands, histogram, percentiles, sampling).

    Returns:
        RasterStatsResult: Per-band statistics with optional histogram.
    """
    # Default params if not provided
    if params is None:
        params = RasterStatsParams()

    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    with rasterio.Env():
        with rasterio.open(uri) as src:
            # Determine which bands to process
            if params.bands is None:
                band_indices = list(range(1, src.count + 1))
            else:
                band_indices = params.bands
                # Validate band indices
                for idx in band_indices:
                    if idx < 1 or idx > src.count:
                        raise ValueError(
                            f"Band index {idx} out of range (1..{src.count})"
                        )

            total_pixels = src.width * src.height
            band_stats_list = []

            for band_idx in band_indices:
                # Read band data (masked if nodata is set)
                if src.nodata is not None:
                    data = src.read(band_idx, masked=True)
                    # Get valid data (unmasked pixels)
                    valid_data = data.compressed()
                    valid_count = len(valid_data)
                    nodata_count = total_pixels - valid_count
                else:
                    data = src.read(band_idx)
                    valid_data = data.ravel()
                    valid_count = len(valid_data)
                    nodata_count = 0

                # Apply sampling if requested for large rasters
                if params.sample_size and valid_count > params.sample_size:
                    # Random sampling for performance
                    rng = np.random.default_rng(42)  # Fixed seed for reproducibility
                    sampled_indices = rng.choice(
                        valid_count, size=params.sample_size, replace=False
                    )
                    valid_data = valid_data[sampled_indices]

                # Compute basic statistics
                if valid_count > 0:
                    min_val = float(np.min(valid_data))
                    max_val = float(np.max(valid_data))
                    mean_val = float(np.mean(valid_data))
                    std_val = float(np.std(valid_data))

                    # Compute percentiles
                    percentile_values = np.percentile(valid_data, params.percentiles)
                    percentile_dict = dict(zip(params.percentiles, percentile_values))
                    
                    median_val = float(percentile_dict.get(50.0, np.median(valid_data)))
                    p25_val = float(percentile_dict.get(25.0)) if 25.0 in percentile_dict else None
                    p75_val = float(percentile_dict.get(75.0)) if 75.0 in percentile_dict else None
                else:
                    min_val = max_val = mean_val = std_val = None
                    median_val = p25_val = p75_val = None

                # Compute histogram if requested
                histogram_bins = []
                if params.include_histogram and valid_count > 0:
                    hist_counts, bin_edges = np.histogram(
                        valid_data, bins=params.histogram_bins
                    )
                    for i, count in enumerate(hist_counts):
                        histogram_bins.append(
                            HistogramBin(
                                min_value=float(bin_edges[i]),
                                max_value=float(bin_edges[i + 1]),
                                count=int(count),
                            )
                        )

                # Build BandStatistics model
                band_stats = BandStatistics(
                    band=band_idx,
                    min=min_val,
                    max=max_val,
                    mean=mean_val,
                    std=std_val,
                    median=median_val,
                    percentile_25=p25_val,
                    percentile_75=p75_val,
                    valid_count=valid_count,
                    nodata_count=nodata_count,
                    histogram=histogram_bins,
                )
                band_stats_list.append(band_stats)

            # Return RasterStatsResult per ADR-0017
            return RasterStatsResult(
                path=uri,
                band_stats=band_stats_list,
                total_pixels=total_pixels,
            )


@mcp.tool(
    name="raster.stats",
    description="Compute detailed statistics for raster bands including min/max/mean/std/percentiles/histogram.",
)
async def raster_stats(
    uri: str,
    params: RasterStatsParams | None = None,
) -> RasterStatsResult:
    """MCP tool wrapper for raster statistics."""
    return await compute_raster_stats(uri, params)
