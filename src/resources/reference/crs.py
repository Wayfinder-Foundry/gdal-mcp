"""Reference resource for common CRS definitions."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import get_common_crs


@mcp.resource("reference://crs/common/{coverage}")
def list_common_crs(
    coverage: str = "all",
    ctx: Context | None = None,
) -> dict:
    """Return curated set of common CRS definitions."""
    normalized = None if not coverage or coverage.lower() == "all" else coverage
    entries = get_common_crs(coverage=normalized)
    if ctx and normalized:
        ctx.debug(f"Filtered common CRS by coverage='{normalized}' -> {len(entries)} entries")

    return {"entries": entries, "total": len(entries)}
