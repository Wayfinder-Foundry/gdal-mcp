"""Vector clipping models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef


class Params(BaseModel):
    """Parameters for vector clipping."""

    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Bounding box [minx, miny, maxx, maxy] for clipping",
    )
    mask: str | None = Field(
        None,
        description="Path to mask geometry file for clipping (alternative to bounds)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a vector clipping operation."""

    output: ResourceRef = Field(description="Reference to the output vector file")
    feature_count: int = Field(ge=0, description="Number of features in output")
    geometry_type: str | None = Field(
        None, description="Primary geometry type (Point, LineString, Polygon, etc.)"
    )
    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Output bounds [minx, miny, maxx, maxy]",
    )
    clip_method: str = Field(description="Clipping method used (bbox or mask)")
