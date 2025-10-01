"""Raster statistics tool using Python-native Rasterio + NumPy."""
from __future__ import annotations

import numpy as np
import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.models.raster.stats import Params, Result, Band, Histogram


async def _stats(
    uri: str,
    params: Params | None = None,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Compute comprehensive statistics for a raster dataset.

    Args:
        uri: Path/URI to the raster dataset.
        params: Statistics parameters (bands, histogram, percentiles, sampling).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Per-band statistics with optional histogram.
    
    Raises:
        ToolError: If raster cannot be opened or parameters are invalid.
    """
    # Default params if not provided
    if params is None:
        params = Params()

    if ctx:
        await ctx.info(f"📂 Opening raster: {uri}")

    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    try:
        with rasterio.Env():
            with rasterio.open(uri) as src:
                if ctx:
                    await ctx.debug(
                        f"✓ Size: {src.width}x{src.height}, Bands: {src.count}, "
                        f"Dtype: {src.dtypes[0] if src.dtypes else 'unknown'}"
                    )
                
                # Determine which bands to process
                if params.bands is None:
                    band_indices = list(range(1, src.count + 1))
                else:
                    band_indices = params.bands
                    # Validate band indices
                    for idx in band_indices:
                        if idx < 1 or idx > src.count:
                            raise ToolError(
                                f"Band index {idx} is out of range. "
                                f"Valid range: 1 to {src.count}. "
                                f"This raster has {src.count} band(s)."
                            )

                total_pixels = src.width * src.height
                band_stats_list = []
                
                if ctx:
                    await ctx.info(f"Computing statistics for {len(band_indices)} band(s)...")
                    await ctx.report_progress(0, len(band_indices))

                for band_num, band_idx in enumerate(band_indices, 1):
                    if ctx:
                        await ctx.debug(f"Processing band {band_idx}...")
                    
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
                        if ctx:
                            await ctx.debug(
                                f"Sampling {params.sample_size} pixels from {valid_count}"
                            )
                        # Random sampling for performance
                        rng = np.random.default_rng(42)  # Fixed seed for reproducibility
                        sampled_indices = rng.choice(
                            valid_count, size=params.sample_size, replace=False
                        )
                        valid_data = valid_data[sampled_indices]

                    # Compute basic statistics
                    min_val: float | None
                    max_val: float | None
                    mean_val: float | None
                    std_val: float | None
                    median_val: float | None
                    p25_val: float | None
                    p75_val: float | None
                    
                    if valid_count > 0:
                        min_val = float(np.min(valid_data))
                        max_val = float(np.max(valid_data))
                        mean_val = float(np.mean(valid_data))
                        std_val = float(np.std(valid_data))

                        # Compute percentiles
                        percentile_values = np.percentile(valid_data, params.percentiles)
                        percentile_dict = dict(zip(params.percentiles, percentile_values))
                        
                        median_val = float(percentile_dict.get(50.0, np.median(valid_data)))
                        p25_val = float(percentile_dict[25.0]) if 25.0 in percentile_dict else None
                        p75_val = float(percentile_dict[75.0]) if 75.0 in percentile_dict else None
                    else:
                        min_val = max_val = mean_val = std_val = None
                        median_val = p25_val = p75_val = None

                    # Compute histogram if requested
                    histogram_bins = []
                    if params.include_histogram and valid_count > 0:
                        if ctx:
                            await ctx.debug(
                                f"Computing histogram with {params.histogram_bins} bins"
                            )
                        hist_counts, bin_edges = np.histogram(
                            valid_data, bins=params.histogram_bins
                        )
                        for i, count in enumerate(hist_counts):
                            histogram_bins.append(
                                Histogram(
                                    min_value=float(bin_edges[i]),
                                    max_value=float(bin_edges[i + 1]),
                                    count=int(count),
                                )
                            )

                    # Build BandStatistics model
                    band_stats = Band(
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
                    
                    if ctx:
                        await ctx.report_progress(band_num, len(band_indices))

                if ctx:
                    await ctx.info("✓ Statistics computation complete")

                # Return RasterStatsResult per ADR-0017
                return Result(
                    path=uri,
                    band_stats=band_stats_list,
                    total_pixels=total_pixels,
                )
    
    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            f"Cannot open raster at '{uri}'. "
            f"Please ensure: (1) file exists, (2) file is a valid raster format. "
            f"Supported formats: GeoTIFF, COG, PNG, JPEG, NetCDF, HDF5. "
            f"Original error: {str(e)}"
        ) from e
    except MemoryError as e:
        raise ToolError(
            f"Out of memory while computing statistics for '{uri}'. "
            f"Try using the 'sample_size' parameter to process a subset of pixels. "
            f"For example: params.sample_size = 1000000 (1 million pixels)."
        ) from e
    except Exception as e:
        raise ToolError(
            f"Unexpected error while computing statistics: {str(e)}"
        ) from e


@mcp.tool(
    name="raster_stats",
    description=(
        "Compute comprehensive statistics for raster bands including "
        "min/max/mean/std/median/percentiles and optional histogram. "
        "USE WHEN: Need to analyze data distribution, find outliers, "
        "understand value ranges, validate data quality, or generate histograms "
        "for visualization. Useful before processing to understand data characteristics. "
        "REQUIRES: uri (path to raster file). "
        "OPTIONAL: params (RasterStatsParams) with bands (list of 1-based indices, "
        "None=all bands), include_histogram (bool, default False), "
        "histogram_bins (2-1024, default 256), percentiles (list like [25, 50, 75]), "
        "sample_size (integer, for large rasters sample random pixels instead of reading all). "
        "OUTPUT: RasterStatsResult with total_pixels and per-band BandStatistics containing "
        "min, max, mean, std, median, percentile_25, percentile_75, valid_count, "
        "nodata_count, and optional histogram (list of HistogramBin with min_value/max_value/count). "
        "SIDE EFFECTS: None (read-only, computes in-memory). "
        "NOTE: Large rasters may require sampling to avoid memory issues."
    ),
)
async def stats(
    uri: str,
    params: Params | None = None,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for raster statistics."""
    return await _stats(uri, params, ctx)
