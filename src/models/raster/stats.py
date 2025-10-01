"""Raster statistics models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Histogram(BaseModel):
    """Single histogram bin."""

    min_value: float = Field(description="Minimum value for this bin")
    max_value: float = Field(description="Maximum value for this bin")
    count: int = Field(ge=0, description="Number of pixels in this bin")


class Band(BaseModel):
    """Statistics for a single raster band."""

    band: int = Field(ge=1, description="Band index (1-based)")
    min: float | None = Field(None, description="Minimum value (excluding nodata)")
    max: float | None = Field(None, description="Maximum value (excluding nodata)")
    mean: float | None = Field(None, description="Mean value (excluding nodata)")
    std: float | None = Field(None, description="Standard deviation (excluding nodata)")
    median: float | None = Field(None, description="Median value (50th percentile)")
    percentile_25: float | None = Field(None, description="25th percentile")
    percentile_75: float | None = Field(None, description="75th percentile")
    valid_count: int = Field(ge=0, description="Number of valid (non-nodata) pixels")
    nodata_count: int = Field(ge=0, description="Number of nodata pixels")
    histogram: list[Histogram] = Field(
        default_factory=list,
        description="Histogram bins (optional)",
    )


class Params(BaseModel):
    """Parameters for raster statistics computation."""

    bands: list[int] | None = Field(
        None,
        description="Band indices to compute stats for (1-based). None = all bands.",
    )
    include_histogram: bool = Field(
        default=False,
        description="Whether to compute histogram (can be expensive for large rasters)",
    )
    histogram_bins: int = Field(
        default=256,
        ge=2,
        le=1024,
        description="Number of histogram bins (2-1024)",
    )
    percentiles: list[float] = Field(
        default_factory=lambda: [25.0, 50.0, 75.0],
        description="Percentiles to compute (0-100)",
    )
    sample_size: int | None = Field(
        None,
        ge=1000,
        description="Sample size for large rasters (None = use all pixels)",
    )


class Result(BaseModel):
    """Result of raster statistics computation."""

    path: str = Field(description="Path to the raster dataset")
    band_stats: list[Band] = Field(description="Per-band statistics")
    total_pixels: int = Field(ge=0, description="Total number of pixels per band")
