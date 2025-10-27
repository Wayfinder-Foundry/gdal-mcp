"""Vector reprojection tool using Python-native pyogrio."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.config import resolve_path
from src.models.resourceref import ResourceRef
from src.models.vector.reproject import Params, Result
from src.shared import vector


async def _reproject(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Reproject a vector dataset to a new CRS.

    Args:
        uri: Path/URI to the source vector dataset (relative or absolute).
        output: Path for the output vector file (relative or absolute).
        params: Reprojection parameters (dst_crs, src_crs override).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the reprojected vector with ResourceRef.

    Raises:
        ToolError: If vector cannot be opened or reprojection fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    if ctx:
        await ctx.info(f"📂 Opening source vector: {uri_path}")
        await ctx.debug(f"Target CRS: {params.dst_crs}")
        if params.src_crs:
            await ctx.debug(f"Source CRS override: {params.src_crs}")
        await ctx.report_progress(0, 100)

    # Per ADR-0013: Delegate to shared logic (pyogrio handles its own context isolation)
    try:
        if ctx:
            await ctx.info("🔄 Reprojecting features...")
            await ctx.report_progress(20, 100)

        # Call shared reprojection logic
        result_data = vector.reproject(
            input_path=uri_path,
            output_path=str(output_path),
            dst_crs=params.dst_crs,
            src_crs=params.src_crs,
            ctx=ctx,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        # Get output file size
        size_bytes = output_path.stat().st_size

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(
                f"✓ Reprojection complete: {output_path} "
                f"({result_data['feature_count']} features, {size_bytes} bytes)"
            )

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver=result_data["driver"],
            meta={
                "src_crs": result_data["src_crs"],
                "dst_crs": params.dst_crs,
                "geometry_type": result_data.get("geometry_type"),
            },
        )

        # Return ReprojectionResult per ADR-0017
        return Result(
            output=resource_ref,
            src_crs=result_data["src_crs"],
            dst_crs=params.dst_crs,
            feature_count=result_data["feature_count"],
            geometry_type=result_data.get("geometry_type"),
            bounds=result_data.get("bounds"),
        )

    except ToolError:
        # Re-raise ToolError as-is
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error during vector reprojection: {e}") from e


@mcp.tool(
    name="vector_reproject",
    description=(
        "Reproject vector dataset to new coordinate reference system. "
        "USE WHEN: Vector CRS doesn't match target projection OR data needs different "
        "spatial reference for analysis, overlay, or web serving. "
        "Common scenarios: convert lat/lon (EPSG:4326) to Web Mercator (EPSG:3857) for web maps, "
        "transform to local UTM zone for accurate area/distance calculations, or align multiple "
        "datasets to common projection for spatial analysis. "
        "REQUIRES: uri (source vector path), output (destination file path), "
        "dst_crs (e.g. 'EPSG:3857', 'EPSG:4326', 'EPSG:32610'). "
        "OPTIONAL: src_crs (override source CRS if missing/incorrect). "
        "OUTPUT: VectorReprojectResult with ResourceRef (output file URI/path/size/metadata), "
        "src_crs used, dst_crs, feature_count, geometry_type, and bounds in destination CRS. "
        "SIDE EFFECTS: Creates new file at output path. "
        "SUPPORTS: Shapefile, GeoPackage, GeoJSON, KML, GML and other OGR formats. "
        "NOTE: Uses pyogrio backend for performance. Reflection middleware will prompt for "
        "CRS selection justification (why this projection? what properties to preserve?) "
        "if not previously justified for this CRS."
    ),
)
async def reproject(
    uri: str,
    output: str,
    dst_crs: str,
    src_crs: str | None = None,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for vector reprojection with flattened parameters.

    Includes reflection preflight for CRS selection justification (reuses same
    reflection as raster_reproject - tests cross-domain cache sharing).
    """
    # Build Params object from flattened parameters
    params = Params(
        dst_crs=dst_crs,
        src_crs=src_crs,
    )
    return await _reproject(uri, output, params, ctx)
