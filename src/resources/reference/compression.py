"""Reference resource for compression methods."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import list_compression_methods


@mcp.resource("reference://compression/available/{kind}")
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
