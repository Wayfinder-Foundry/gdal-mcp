"""Reference resource for compression methods."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import list_compression_methods


@mcp.resource(
    uri="reference://compression/available/{kind}",
    name="Compression Methods Reference",
    description=(
        "Available raster compression methods with detailed guidance on when to use each. "
        "Provides comprehensive information about compression algorithms including lossless "
        "(LZW, DEFLATE, ZSTD, PACKBITS) and lossy (JPEG, WEBP) methods. Includes trade-offs "
        "between compression ratio, speed, and compatibility. Essential for raster_convert "
        "operations to optimize file size while preserving data quality."
    ),
)
def list_compression_methods_resource(
    kind: str = "all",
    ctx: Context | None = None,
) -> dict:
    """Return curated list of raster compression methods."""
    entries = list_compression_methods()
    if ctx and kind and kind.lower() != "all":
        ctx.debug(
            "Compression resource currently ignores 'kind' filter; "
            f"received '{kind}', returning full set"
        )
    return {"entries": entries, "total": len(entries)}
