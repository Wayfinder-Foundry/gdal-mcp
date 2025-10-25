"""Reference resource for common CRS definitions."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import get_common_crs


@mcp.resource(
    uri="reference://crs/common/{coverage}",
    name="Common CRS Reference",
    description=(
        "Curated reference of commonly-used coordinate reference systems organized by use case "
        "and geographic coverage. Includes global systems (EPSG:4326, EPSG:3857), continental "
        "projections, and regional UTM zones. Provides EPSG codes, names, areas of use, and "
        "guidance on appropriate applications. Essential for raster_reproject and vector_reproject "
        "operations to select appropriate target coordinate systems. Filter by coverage: "
        "'global', 'continental', 'utm', or 'all'."
    ),
)
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
