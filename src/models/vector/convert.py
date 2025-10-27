"""Vector format conversion models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef


class Params(BaseModel):
    """Parameters for vector format conversion."""

    driver: str | None = Field(
        None,
        description="Output driver (auto-detected from extension if None). "
        "Options: 'ESRI Shapefile', 'GPKG', 'GeoJSON', 'KML', 'GML'",
    )
    encoding: str = Field(
        "UTF-8",
        description="Character encoding for output (UTF-8 recommended, "
        "ISO-8859-1 for legacy shapefile compatibility)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a vector format conversion operation."""

    output: ResourceRef = Field(description="Reference to the output vector file")
    src_driver: str = Field(description="Source driver detected")
    dst_driver: str = Field(description="Destination driver used")
    feature_count: int = Field(ge=0, description="Number of features converted")
    geometry_type: str | None = Field(
        None, description="Primary geometry type (Point, LineString, Polygon, etc.)"
    )
    encoding: str = Field(description="Character encoding used")
