"""Raster conversion models."""
from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.common import Compression, ResourceRef


class ConversionOptions(BaseModel):
    """Options for raster format conversion."""

    driver: str = Field(
        default="GTiff",
        description="Output driver (GTiff, COG, PNG, JPEG, etc.)",
    )
    compression: Compression | None = Field(
        None,
        description="Compression method (none, lzw, deflate, zstd, jpeg, packbits)",
    )
    tiled: bool = Field(
        default=True,
        description="Create tiled output (improves performance for large rasters)",
    )
    blockxsize: int = Field(
        default=256,
        ge=16,
        description="Tile width in pixels (must be multiple of 16)",
    )
    blockysize: int = Field(
        default=256,
        ge=16,
        description="Tile height in pixels (must be multiple of 16)",
    )
    photometric: str | None = Field(
        None,
        description="Photometric interpretation (RGB, YCBCR, MINISBLACK, etc.)",
    )
    overviews: list[int] = Field(
        default_factory=list,
        description="Overview levels to build (e.g., [2, 4, 8, 16])",
    )
    overview_resampling: str = Field(
        default="average",
        description="Resampling method for overviews",
    )
    creation_options: dict[str, str] = Field(
        default_factory=dict,
        description="Additional driver-specific creation options",
    )

    class Config:
        use_enum_values = True


class ConversionResult(BaseModel):
    """Result of a raster conversion operation."""

    output: ResourceRef = Field(description="Reference to the output raster file")
    driver: str = Field(description="Driver used for output")
    compression: str | None = Field(None, description="Compression applied")
    size_bytes: int = Field(ge=0, description="Output file size in bytes")
    overviews_built: list[int] = Field(
        default_factory=list, description="Overview levels that were built"
    )
