"""Raster reprojection models."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.common import ResamplingMethod, ResourceRef


class ReprojectionParams(BaseModel):
    """Parameters for raster reprojection."""

    dst_crs: str = Field(
        description="Destination CRS (e.g., EPSG:4326, EPSG:3857)",
        pattern=r"^(EPSG:\d+|[A-Z]+:.+)$",
    )
    resampling: ResamplingMethod = Field(
        description="Resampling method (per ADR-0011: explicit required)",
    )
    src_crs: str | None = Field(
        None,
        description="Source CRS override (auto-detected if None)",
    )
    resolution: tuple[float, float] | None = Field(
        None,
        description="Output resolution as (x_res, y_res) in destination CRS units",
    )
    width: int | None = Field(
        None,
        ge=1,
        description="Output width in pixels (mutually exclusive with resolution)",
    )
    height: int | None = Field(
        None,
        ge=1,
        description="Output height in pixels (mutually exclusive with resolution)",
    )
    bounds: tuple[float, float, float, float] | None = Field(
        None,
        description="Output bounds (left, bottom, right, top) in destination CRS",
    )
    nodata: float | None = Field(
        None,
        description="NoData value for output (preserves source nodata if None)",
    )

    class Config:
        use_enum_values = True


class ReprojectionResult(BaseModel):
    """Result of a raster reprojection operation."""

    output: ResourceRef = Field(description="Reference to the output raster file")
    src_crs: str = Field(description="Source CRS that was used")
    dst_crs: str = Field(description="Destination CRS")
    resampling: str = Field(description="Resampling method applied")
    transform: list[float] = Field(
        min_length=6,
        max_length=6,
        description="Affine transform of output as [a, b, c, d, e, f]",
    )
    width: int = Field(ge=1, description="Output width in pixels")
    height: int = Field(ge=1, description="Output height in pixels")
    bounds: tuple[float, float, float, float] = Field(
        description="Output bounds (left, bottom, right, top) in dst_crs"
    )
