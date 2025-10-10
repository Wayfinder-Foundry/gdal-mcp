"""Reference resource for resampling methods."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import list_resampling_methods, resampling_guide


@mcp.resource("reference://resampling/available/{category}")
def list_resampling_methods_resource(
    category: str = "all",
    ctx: Context | None = None,
) -> dict:
    """Return available resampling methods and usage guidance."""
    normalized = None if not category or category.lower() == "all" else category
    entries = list_resampling_methods(category=normalized)
    if ctx and normalized:
        ctx.debug(
            f"Filtered resampling methods by category='{normalized}' -> {len(entries)} entries"
        )

    return {"entries": entries, "total": len(entries)}


@mcp.resource("reference://resampling/guide/{method}")
def resampling_guide_resource(
    method: str = "all",
    ctx: Context | None = None,
) -> dict:
    """Return curated guide for choosing resampling strategies."""
    normalized = None if not method or method.lower() == "all" else method
    entries = resampling_guide(topic=normalized)
    if ctx and normalized:
        ctx.debug(f"Filtered resampling guide by method='{normalized}' -> {len(entries)} entries")

    return {"entries": entries, "total": len(entries)}
