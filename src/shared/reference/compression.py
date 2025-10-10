"""Compression method reference data for raster operations."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict

try:  # Python 3.11+
    from enum import StrEnum
except ImportError:  # pragma: no cover - backport for Python 3.10
    class StrEnum(str, Enum):
        """Minimal StrEnum backport for Python < 3.11."""

        pass


class CompressionInfo(TypedDict):
    """Structured description of a GDAL-compatible raster compression method."""

    name: str
    description: str
    best_for: str
    lossless: bool


class Compression(StrEnum):
    """GDAL-supported compression methods."""

    LZW = "LZW"
    DEFLATE = "DEFLATE"
    ZSTD = "ZSTD"
    JPEG = "JPEG"
    WEBP = "WEBP"
    LERC = "LERC"
    PACKBITS = "PACKBITS"


# Central registry — use consistent naming & include lossless flag
_COMPRESSION_METHODS: list[CompressionInfo] = [
    {
        "name": Compression.LZW,
        "description": "Lempel–Ziv–Welch compression. Balanced speed/ratio.",
        "best_for": "General-purpose lossless compression for GeoTIFF rasters.",
        "lossless": True,
    },
    {
        "name": Compression.DEFLATE,
        "description": "Zlib/Deflate-based lossless compression with optional predictor.",
        "best_for": "Continuous rasters needing lossless compression and predictor tuning.",
        "lossless": True,
    },
    {
        "name": Compression.ZSTD,
        "description": "Zstandard lossless compression (GDAL ≥ 3.1).",
        "best_for": "High compression ratios with good performance; flexible tuning via ZLEVEL.",
        "lossless": True,
    },
    {
        "name": Compression.JPEG,
        "description": "Lossy JPEG baseline compression (requires 8-bit BYTE data).",
        "best_for": (
            "Natural imagery where small loss is acceptable and space savings are important."
        ),
        "lossless": False,
    },
    {
        "name": Compression.WEBP,
        "description": "WebP compression (lossy or lossless). Supports alpha channel.",
        "best_for": "RGBA imagery, especially web-served raster tiles.",
        "lossless": False,  # could be True if using lossless mode, but keep simple
    },
    {
        "name": Compression.LERC,
        "description": "Limited Error Raster Compression (supports lossy or lossless).",
        "best_for": "Continuous datasets (e.g., elevation) with small error tolerance.",
        "lossless": True,  # can be lossy depending on usage
    },
    {
        "name": Compression.PACKBITS,
        "description": "Run-length encoding; very fast but low ratio.",
        "best_for": "Binary or sparse data (e.g., masks).",
        "lossless": True,
    },
]


def list_compression_methods() -> list[CompressionInfo]:
    """
    Return curated list of GDAL-compatible raster compression methods.

    Each entry includes:
      - name: GDAL compression identifier
      - description: Human-readable summary
      - best_for: Usage guidance
      - lossless: Whether the method is typically lossless
    """
    return list(_COMPRESSION_METHODS)
