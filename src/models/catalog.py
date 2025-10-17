"""Catalog data models for workspace dataset discovery."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, conint


class CatalogResponse(BaseModel):
    """Response payload for workspace catalog resources."""

    kind: Literal["raster", "vector", "other"] | None = Field(
        default=None,
        description="Classification applied to returned entries, if filtered.",
    )
    entries: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of catalogued workspace entries.",
    )
    total: conint(ge=0) = Field(
        description="Total number of entries included in this response.",
    )
