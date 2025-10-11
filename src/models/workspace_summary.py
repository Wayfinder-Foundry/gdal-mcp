"""Workspace summary data models for high-level workspace overview."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DatasetCount(BaseModel):
    """Count of datasets by type."""

    raster: int = Field(default=0, ge=0, description="Number of raster datasets")
    vector: int = Field(default=0, ge=0, description="Number of vector datasets")
    other: int = Field(default=0, ge=0, description="Number of other files")
    total: int = Field(default=0, ge=0, description="Total number of files")


class CRSDistribution(BaseModel):
    """Distribution of coordinate reference systems across datasets."""

    crs_code: str = Field(description="CRS identifier (e.g., EPSG:4326)")
    count: int = Field(ge=1, description="Number of datasets using this CRS")
    percentage: float = Field(ge=0, le=100, description="Percentage of total datasets")


class FormatDistribution(BaseModel):
    """Distribution of file formats across datasets."""

    format_name: str = Field(description="Format name (e.g., GTiff, GeoJSON)")
    extension: str = Field(description="File extension (e.g., .tif, .geojson)")
    count: int = Field(ge=1, description="Number of files with this format")
    percentage: float = Field(ge=0, le=100, description="Percentage of total files")


class SizeStatistics(BaseModel):
    """Size statistics for workspace datasets."""

    total_bytes: int = Field(ge=0, description="Total size in bytes")
    total_mb: float = Field(ge=0, description="Total size in megabytes")
    total_gb: float = Field(ge=0, description="Total size in gigabytes")
    average_bytes: float = Field(ge=0, description="Average file size in bytes")
    largest_file: str | None = Field(default=None, description="Path to largest file")
    largest_size_mb: float | None = Field(default=None, description="Size of largest file in MB")


class WorkspaceSummary(BaseModel):
    """High-level summary of workspace contents."""

    workspaces: list[str] = Field(description="List of configured workspace paths")
    dataset_counts: DatasetCount = Field(description="Count of datasets by type")
    crs_distribution: list[CRSDistribution] = Field(
        default_factory=list,
        description="Distribution of CRS across datasets",
    )
    format_distribution: list[FormatDistribution] = Field(
        default_factory=list,
        description="Distribution of formats across datasets",
    )
    size_statistics: SizeStatistics = Field(description="Size statistics for datasets")
    scan_timestamp: str = Field(description="ISO 8601 timestamp of scan")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the scan",
    )
