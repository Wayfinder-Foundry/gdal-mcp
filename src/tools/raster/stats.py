"""Raster statistics tool using Python-native Rasterio + NumPy."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.config import resolve_path
from src.models.raster.stats import Band, Histogram, Params, Result
from src.shared.raster.stats import stats as extract_raster_stats


async def _stats(
    uri: str,
    params: Params | None = None,
    ctx: Context | None = None,
) -> Result:
    """Compute statistics using shared extractor and map to Result model."""
    # Resolve path to absolute
    uri_path = str(resolve_path(uri))

    params_dict = params.model_dump() if params is not None else None
    data = extract_raster_stats(uri_path, params_dict, ctx)

    band_models: list[Band] = []
    for b in data.get("band_stats", []):
        hist_models: list[Histogram] = []
        for hb in b.get("histogram", []):
            hist_models.append(
                Histogram(
                    min_value=float(hb["min_value"]),
                    max_value=float(hb["max_value"]),
                    count=int(hb["count"]),
                )
            )
        band_models.append(
            Band(
                band=int(b["band"]),
                min=b.get("min"),
                max=b.get("max"),
                mean=b.get("mean"),
                std=b.get("std"),
                median=b.get("median"),
                percentile_25=b.get("percentile_25"),
                percentile_75=b.get("percentile_75"),
                valid_count=int(b.get("valid_count", 0)),
                nodata_count=int(b.get("nodata_count", 0)),
                histogram=hist_models,
            )
        )

    return Result(
        path=str(data.get("path", uri)),
        band_stats=band_models,
        total_pixels=int(data.get("total_pixels", 0)),
    )


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
        "nodata_count, and optional histogram "
        "(list of HistogramBin with min_value/max_value/count). "
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
