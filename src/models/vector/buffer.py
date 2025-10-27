"""Vector buffer models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef


class Params(BaseModel):
    """Parameters for vector buffering."""

    distance: float = Field(
        description="Buffer distance in CRS units (meters for projected, degrees for geographic)",
        gt=0,
    )
    resolution: int = Field(
        16,
        ge=4,
        le=64,
        description="Segments per quadrant for buffer polygon (higher = smoother, slower)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a vector buffer operation."""

    output: ResourceRef = Field(description="Reference to the output vector file")
    feature_count: int = Field(ge=0, description="Number of features buffered")
    buffer_distance: float = Field(description="Buffer distance applied")
    resolution: int = Field(description="Segments per quadrant used")
    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Output bounds [minx, miny, maxx, maxy]",
    )
