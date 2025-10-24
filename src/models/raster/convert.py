"""Raster conversion models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models.resourceref import ResourceRef

# Define compression methods as a literal type for better MCP serialization
# Note: Values are lowercase to match rasterio.enums.Compression
CompressionMethod = Literal[
    "jpeg",
    "lzw",
    "packbits",
    "deflate",
    "ccittrle",
    "ccittfax3",
    "ccittfax4",
    "lzma",
    "none",
    "zstd",
    "lerc",
    "lerc_deflate",
    "lerc_zstd",
    "webp",
    "jpeg2000",
]


class Options(BaseModel):
    """Options for raster format conversion."""

    driver: str = Field(
        default="GTiff",
        description="Output driver (GTiff, COG, PNG, JPEG, etc.)",
    )
    compression: CompressionMethod | None = Field(
        None,
        description=(
            "Compression method (lowercase). "
            "See reference://compression/available/all for full list with guidance. "
            "Common options: deflate (universal, lossless), lzw (GeoTIFF, categorical), "
            "zstd (modern, fast, GDAL 3.4+), jpeg (lossy, RGB only), none (no compression). "
            "Driver compatibility varies - deflate works with most formats."
        ),
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
    )
    overview_resampling: str = Field(
        default="average",
        description="Resampling method for overviews",
    )
    creation_options: dict[str, str | int | float] = Field(
        default_factory=dict,
        description="Additional driver-specific creation options",
    )

    model_config = ConfigDict()


class Result(BaseModel):
    """Result of a raster conversion operation."""

    output: ResourceRef = Field(description="Reference to the output raster file")
    driver: str = Field(description="Driver used for output")
    compression: str | None = Field(None, description="Compression applied")
    size_bytes: int = Field(ge=0, description="Output file size in bytes")
    overviews_built: list[int] = Field(
        default_factory=list, description="Overview levels that were built"
    )
