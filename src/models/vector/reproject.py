"""Vector reprojection models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef


class Params(BaseModel):
    """Parameters for vector reprojection."""

    dst_crs: str = Field(
        description="Destination CRS (e.g., 'EPSG:4326', 'EPSG:3857')",
        pattern=r"^(EPSG:\d+|[A-Z]+:.+)$",
    )
    src_crs: str | None = Field(
        None,
        description="Source CRS override (auto-detected if None)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a vector reprojection operation."""

    output: ResourceRef = Field(description="Reference to the output vector file")
    src_crs: str = Field(description="Source CRS that was used")
    dst_crs: str = Field(description="Destination CRS")
    feature_count: int = Field(ge=0, description="Number of features in output")
    geometry_type: str | None = Field(
        None, description="Primary geometry type (Point, LineString, Polygon, etc.)"
    )
    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Output bounds [minx, miny, maxx, maxy] in dst_crs",
    )
