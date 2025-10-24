"""Raster conversion models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator
from rasterio.enums import Compression

from src.models.resourceref import ResourceRef


class Options(BaseModel):
    """Options for raster format conversion."""

    driver: str = Field(
        default="GTiff",
        description="Output driver (GTiff, COG, PNG, JPEG, etc.)",
    )
    compression: Compression | None = Field(
        None,
        description=(
            "Compression method (case-insensitive). "
            "See reference://compression/available/all for full list with guidance. "
            "Common options: DEFLATE (universal, lossless), LZW (GeoTIFF, categorical), "
            "ZSTD (modern, fast, GDAL 3.4+), JPEG (lossy, RGB only), NONE (no compression). "
            "Driver compatibility varies - DEFLATE works with most formats."
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

    @field_validator("compression", mode="before")
    @classmethod
    def normalize_compression(cls, v: str | Compression | None) -> Compression | None:
        """Normalize compression to lowercase for case-insensitive matching.

        Note: Rasterio's Compression enum uses lowercase values (deflate, lzw, etc.)
        but our reference resource documents them as uppercase for clarity.
        This validator accepts both cases.
        """
        if v is None:
            return None
        if isinstance(v, Compression):
            return v
        # Convert string to lowercase to match rasterio enum values
        return Compression[v.lower()]

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
