"""CRS-filtered catalog resource."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.models.catalog import CatalogResponse
from src.shared.catalog import filter_by_crs


@mcp.resource("catalog://workspace/by-crs/{epsg}{?kind,include_hidden}")
def list_by_crs(
    epsg: str,
    kind: str = "all",
    include_hidden: bool = False,
    ctx: Context | None = None,
) -> dict:
    """List all datasets in the workspace that use a specific CRS.

    This resource enables AI to discover all data in a particular coordinate system,
    which is critical for multi-step workflows requiring CRS consistency.

    Use cases:
    - Finding all data in Web Mercator (EPSG:3857) for web mapping
    - Discovering WGS84 (EPSG:4326) datasets for global analysis
    - Identifying datasets that need reprojection to align with target CRS
    - Planning batch operations on datasets with the same projection

    Args:
        epsg: CRS identifier (e.g., "EPSG:4326", "4326", "EPSG:3857")
        kind: Filter by dataset type ("all", "raster", "vector")
        include_hidden: Whether to include hidden files
        ctx: Optional context for logging

    Returns:
        Catalog response with filtered entries

    Examples:
        - catalog://workspace/by-crs/4326 - All WGS84 datasets
        - catalog://workspace/by-crs/3857?kind=raster - Web Mercator rasters only
        - catalog://workspace/by-crs/EPSG:32610 - UTM Zone 10N datasets
    """
    if ctx:
        ctx.info(f"[catalog://workspace/by-crs] Filtering for CRS: {epsg}, kind: {kind}")

    entries = filter_by_crs(
        crs_code=epsg,
        kind=kind,
        include_hidden=include_hidden,
        ctx=ctx,
    )

    response = CatalogResponse(
        kind=None if kind == "all" else kind,
        entries=[entry.to_dict() for entry in entries],
        total=len(entries),
    )

    return response.model_dump()
