"""Raster reprojection models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef

# Define resampling methods as a literal type for better MCP serialization
ResamplingMethod = Literal[
    "nearest",
    "bilinear",
    "cubic",
    "cubic_spline",
    "lanczos",
    "average",
    "mode",
    "gauss",
]


class Params(BaseModel):
    """Parameters for raster reprojection."""

    dst_crs: str = Field(
        description="Destination CRS (e.g., 'EPSG:4326', 'EPSG:3857')",
        pattern=r"^(EPSG:\d+|[A-Z]+:.+)$",
    )
    resampling: ResamplingMethod = Field(
        description=(
            "Resampling method (per ADR-0011: explicit required). "
            "Options: nearest (categorical data), bilinear (continuous data), "
            "cubic (smooth continuous data), cubic_spline, lanczos, average, mode, gauss"
        ),
    )
    src_crs: str | None = Field(
        None,
        description="Source CRS override (auto-detected if None)",
    )
    resolution: list[float] | None = Field(
        None,
        min_length=2,
        max_length=2,
        description="Output resolution as [x_res, y_res] in destination CRS units",
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
    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Output bounds [left, bottom, right, top] in destination CRS",
    )
    nodata: float | None = Field(
        None,
        description="NoData value for output (preserves source nodata if None)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
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
    bounds: list[float] = Field(
        min_length=4,
        max_length=4,
        description="Output bounds [left, bottom, right, top] in dst_crs",
    )
