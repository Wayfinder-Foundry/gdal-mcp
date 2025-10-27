"""Vector simplification tool using Python-native pyogrio and shapely."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.config import resolve_path
from src.models.resourceref import ResourceRef
from src.models.vector.simplify import Params, Result
from src.shared import vector


async def _simplify(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Simplify vector geometries.

    Args:
        uri: Path/URI to the source vector dataset (relative or absolute).
        output: Path for the output vector file (relative or absolute).
        params: Simplification parameters (tolerance, method, preserve_topology).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the simplified vector with ResourceRef.

    Raises:
        ToolError: If vector cannot be opened or simplification fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    if ctx:
        await ctx.info(f"📂 Opening source vector: {uri_path}")
        await ctx.debug(
            f"Tolerance: {params.tolerance}, method: {params.method}, "
            f"preserve_topology: {params.preserve_topology}"
        )
        await ctx.report_progress(0, 100)

    # Per ADR-0013: Delegate to shared logic
    try:
        if ctx:
            await ctx.info("🔧 Simplifying geometries...")
            await ctx.report_progress(20, 100)

        # Call shared simplification logic
        result_data = vector.simplify(
            input_path=uri_path,
            output_path=str(output_path),
            tolerance=params.tolerance,
            method=params.method,
            preserve_topology=params.preserve_topology,
            ctx=ctx,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        # Get output file size
        size_bytes = output_path.stat().st_size

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(
                f"✓ Simplification complete: {output_path} "
                f"({result_data['feature_count']} features, {size_bytes} bytes)"
            )

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver="auto",
            meta={
                "tolerance": params.tolerance,
                "method": params.method,
                "preserve_topology": params.preserve_topology,
            },
        )

        # Return SimplifyResult
        return Result(
            output=resource_ref,
            feature_count=result_data["feature_count"],
            tolerance=result_data["tolerance"],
            method=result_data["method"],
            preserve_topology=result_data["preserve_topology"],
            bounds=result_data.get("bounds"),
        )

    except ToolError:
        # Re-raise ToolError as-is
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error during vector simplification: {e}") from e


@mcp.tool(
    name="vector_simplify",
    description=(
        "Simplify vector geometries to reduce complexity and file size for web display "
        "or generalization. "
        "USE WHEN: Need to reduce vertex count, optimize for web mapping, create "
        "generalized representations, or reduce file size while preserving shape. "
        "Common scenarios: Web map optimization (reduce vertices for faster rendering), "
        "multi-scale mapping (create simplified versions for zoom levels), "
        "file size reduction (large detailed datasets). "
        "REQUIRES: uri (source vector path), output (destination file path), "
        "tolerance (simplification distance in CRS units - larger = more simplified). "
        "OPTIONAL: method (douglas-peucker default, or visvalingam), "
        "preserve_topology (True default - ensures valid geometries). "
        "OUTPUT: VectorSimplifyResult with ResourceRef (output file URI/path/size/metadata), "
        "feature_count, tolerance applied, method used, preserve_topology flag, bounds. "
        "SIDE EFFECTS: Creates new file at output path. Reduces vertex count. "
        "SUPPORTS: Shapefile, GeoPackage, GeoJSON and other OGR formats. "
        "METHODS: Douglas-Peucker (fast, standard) removes points based on perpendicular "
        "distance; Visvalingam-Whyatt (slower, preserves shape) removes points based on "
        "area. TOLERANCE: Measured in CRS units - for EPSG:4326 use 0.0001-0.01 degrees, "
        "for projected CRS use 10-1000 meters depending on scale. Higher tolerance = "
        "more simplification. Uses shapely for geometry operations. "
        "No reflection required - tolerance is user-specified based on use case."
    ),
)
async def simplify(
    uri: str,
    output: str,
    tolerance: float,
    method: str = "douglas-peucker",
    preserve_topology: bool = True,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for vector simplification with flattened parameters.

    No reflection middleware - tolerance selection is user-directed based on
    target scale and use case.
    """
    # Build Params object from flattened parameters
    params = Params(
        tolerance=tolerance,
        method=method,  # type: ignore[arg-type]
        preserve_topology=preserve_topology,
    )
    return await _simplify(uri, output, params, ctx)
