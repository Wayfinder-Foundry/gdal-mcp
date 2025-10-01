"""Common models and enums shared across raster and vector operations."""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResourceRef(BaseModel):
    """Reference to a generated resource (file, URI, embedded data)."""

    uri: str = Field(description="Resource URI (file://, s3://, http://, etc.)")
    path: str | None = Field(None, description="Local filesystem path if applicable")
    size: int | None = Field(None, ge=0, description="Size in bytes")
    checksum: str | None = Field(None, description="Checksum (e.g., SHA256)")
    driver: str | None = Field(None, description="GDAL driver name")
    meta: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ResamplingMethod(str, Enum):
    """Resampling methods for raster operations (ADR-0011)."""

    NEAREST = "nearest"
    BILINEAR = "bilinear"
    CUBIC = "cubic"
    CUBIC_SPLINE = "cubic_spline"
    LANCZOS = "lanczos"
    AVERAGE = "average"
    MODE = "mode"
    GAUSS = "gauss"


class Compression(str, Enum):
    """Compression methods for raster outputs."""

    NONE = "none"
    LZW = "lzw"
    DEFLATE = "deflate"
    ZSTD = "zstd"
    JPEG = "jpeg"
    PACKBITS = "packbits"
