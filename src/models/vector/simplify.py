"""Vector simplification models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef

SimplifyMethod = Literal["douglas-peucker", "visvalingam"]


class Params(BaseModel):
    """Parameters for vector simplification."""

    tolerance: float = Field(
        description="Simplification tolerance in CRS units (larger = more simplified)",
        gt=0,
    )
    method: SimplifyMethod = Field(
        "douglas-peucker",
        description="Simplification algorithm: douglas-peucker (default, fast) or "
        "visvalingam (area-based, preserves shape better)",
    )
    preserve_topology: bool = Field(
        True,
        description="Ensure output geometries are valid (no self-intersections)",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a vector simplification operation."""

    output: ResourceRef = Field(description="Reference to the output vector file")
    feature_count: int = Field(ge=0, description="Number of features simplified")
    tolerance: float = Field(description="Tolerance applied")
    method: str = Field(description="Simplification method used")
    preserve_topology: bool = Field(description="Whether topology was preserved")
    bounds: list[float] | None = Field(
        None,
        min_length=4,
        max_length=4,
        description="Output bounds [minx, miny, maxx, maxy]",
    )
