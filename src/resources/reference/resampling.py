"""Reference resource for resampling methods."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import list_resampling_methods, resampling_guide


@mcp.resource(
    uri="reference://resampling/available/{category}",
    name="Resampling Methods Available",
    description=(
        "Complete enumeration of available resampling methods from rasterio.enums.Resampling. "
        "Lists all supported algorithms including nearest, bilinear, cubic, cubic_spline, lanczos, "
        "average, mode, gauss, and max/min/med/q1/q3. Used by raster_reproject and raster_convert "
        "with overviews. Filter by category: 'interpolation', 'aggregation', or 'all'."
    ),
)
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


@mcp.resource(
    uri="reference://resampling/guide/{method}",
    name="Resampling Selection Guide",
    description=(
        "Expert guidance for choosing appropriate resampling methods based on data type and "
        "use case. Explains trade-offs between interpolation quality, performance, and data "
        "integrity. Critical for raster_reproject operations per ADR-0011 requirement. "
        "Covers: nearest (categorical/discrete data, preserves exact values), bilinear "
        "(continuous data, smooth results), cubic (elevation/scientific, highest quality), "
        "average (downsampling), mode (categorical downsampling). Filter by method name or 'all'."
    ),
)
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
