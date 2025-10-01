"""Common models and enums shared across raster and vector operations."""
from __future__ import annotations

from enum import Enum


class Compression(str, Enum):
    """Compression methods for raster outputs."""

    NONE = "none"
    LZW = "lzw"
    DEFLATE = "deflate"
    ZSTD = "zstd"
    JPEG = "jpeg"
    PACKBITS = "packbits"
