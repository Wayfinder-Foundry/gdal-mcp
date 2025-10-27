"""Vector clipping tool using Python-native pyogrio and shapely."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.config import resolve_path
from src.models.resourceref import ResourceRef
from src.models.vector.clip import Params, Result
from src.shared import vector


async def _clip(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Clip a vector dataset by bounding box or mask.

    Args:
        uri: Path/URI to the source vector dataset (relative or absolute).
        output: Path for the output vector file (relative or absolute).
        params: Clipping parameters (bounds or mask).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the clipped vector with ResourceRef.

    Raises:
        ToolError: If vector cannot be opened or clipping fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    # Resolve mask path if provided
    mask_path = str(resolve_path(params.mask)) if params.mask else None

    if ctx:
        await ctx.info(f"📂 Opening source vector: {uri_path}")
        if params.bounds:
            await ctx.debug(f"Clipping by bounds: {params.bounds}")
        elif params.mask:
            await ctx.debug(f"Clipping by mask: {mask_path}")
        await ctx.report_progress(0, 100)

    # Per ADR-0013: Delegate to shared logic
    try:
        if ctx:
            await ctx.info("✂️ Clipping features...")
            await ctx.report_progress(20, 100)

        # Call shared clipping logic
        result_data = vector.clip(
            input_path=uri_path,
            output_path=str(output_path),
            bounds=params.bounds,
            mask=mask_path,
            ctx=ctx,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        # Get output file size
        size_bytes = output_path.stat().st_size

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(
                f"✓ Clipping complete: {output_path} "
                f"({result_data['feature_count']} features retained, {size_bytes} bytes)"
            )

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver="auto",  # Driver determined by extension in shared logic
            meta={
                "clip_method": result_data["clip_method"],
                "feature_count": result_data["feature_count"],
            },
        )

        # Return ClipResult
        return Result(
            output=resource_ref,
            feature_count=result_data["feature_count"],
            geometry_type=result_data.get("geometry_type"),
            bounds=result_data.get("bounds"),
            clip_method=result_data["clip_method"],
        )

    except ToolError:
        # Re-raise ToolError as-is
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error during vector clipping: {e}") from e


@mcp.tool(
    name="vector_clip",
    description=(
        "Clip vector dataset by bounding box or mask geometry for spatial subsetting. "
        "USE WHEN: Need to extract features within specific area, subset large datasets, "
        "or prepare data for localized analysis. "
        "Common scenarios: Clip to study area extent, extract features within city boundary, "
        "subset regional data to project area. "
        "REQUIRES: uri (source vector path), output (destination file path). "
        "ONE OF: bounds=[minx, miny, maxx, maxy] (bounding box) OR mask=<path> (clip geometry). "
        "OUTPUT: VectorClipResult with ResourceRef (output file URI/path/size/metadata), "
        "feature_count (features in output), geometry_type, bounds, clip_method used. "
        "SIDE EFFECTS: Creates new file at output path. "
        "SUPPORTS: Shapefile, GeoPackage, GeoJSON and other OGR formats. "
        "NOTE: Features intersecting clip boundary are split. Empty geometries removed. "
        "Uses pyogrio and shapely for performance. No reflection required - spatial "
        "operations are straightforward with user-defined extents."
    ),
)
async def clip(
    uri: str,
    output: str,
    bounds: list[float] | None = None,
    mask: str | None = None,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for vector clipping with flattened parameters.

    No reflection middleware - spatial subsetting is user-directed with
    explicit bounds or mask geometry.
    """
    # Build Params object from flattened parameters
    params = Params(
        bounds=bounds,
        mask=mask,
    )
    return await _clip(uri, output, params, ctx)
