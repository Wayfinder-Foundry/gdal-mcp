"""Vector info model."""
from __future__ import annotations

from pydantic import BaseModel, Field


class VectorInfo(BaseModel):
    """Structured metadata for a vector dataset."""

    path: str = Field(description="Path or URI to the vector dataset")
    driver: str | None = Field(None, description="GDAL/OGR driver name (e.g., GPKG)")
    crs: str | None = Field(None, description="Coordinate reference system (e.g., EPSG:4326)")
    layer_count: int | None = Field(None, ge=1, description="Number of layers")
    geometry_types: list[str] = Field(
        default_factory=list, description="Geometry types present (e.g., Point, Polygon)"
    )
    feature_count: int | None = Field(None, ge=0, description="Total feature count")
    fields: list[tuple[str, str]] = Field(
        default_factory=list, description="Field names and types as (name, type) tuples"
    )
    bounds: tuple[float, float, float, float] | None = Field(
        None, description="Bounding box as (minx, miny, maxx, maxy)"
    )
