"""Raster info model."""
from __future__ import annotations

from pydantic import BaseModel, Field


class Info(BaseModel):
    """Structured metadata for a raster dataset."""

    path: str = Field(description="Path or URI to the raster dataset")
    driver: str | None = Field(None, description="GDAL driver name (e.g., GTiff)")
    crs: str | None = Field(None, description="Coordinate reference system (e.g., EPSG:4326)")
    width: int = Field(ge=1, description="Raster width in pixels")
    height: int = Field(ge=1, description="Raster height in pixels")
    count: int = Field(ge=1, description="Number of bands")
    dtype: str | None = Field(None, description="Data type of first band")
    transform: list[float] = Field(
        min_length=6,
        max_length=6,
        description="Affine transform as [a, b, c, d, e, f]",
    )
    bounds: tuple[float, float, float, float] = Field(
        description="Bounding box as (left, bottom, right, top)"
    )
    nodata: float | None = Field(None, description="NoData value")
    overview_levels: list[int] = Field(
        default_factory=list, description="Overview/pyramid levels"
    )
    tags: dict[str, str] = Field(default_factory=dict, description="Raster tags/metadata")
