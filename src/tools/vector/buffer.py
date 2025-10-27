"""Vector buffer tool using Python-native pyogrio and shapely."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.config import resolve_path
from src.models.resourceref import ResourceRef
from src.models.vector.buffer import Params, Result
from src.shared import vector


async def _buffer(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Create buffer around vector geometries.

    Args:
        uri: Path/URI to the source vector dataset (relative or absolute).
        output: Path for the output vector file (relative or absolute).
        params: Buffer parameters (distance, resolution).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the buffered vector with ResourceRef.

    Raises:
        ToolError: If vector cannot be opened or buffering fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    if ctx:
        await ctx.info(f"📂 Opening source vector: {uri_path}")
        await ctx.debug(f"Buffer distance: {params.distance}, resolution: {params.resolution}")
        await ctx.report_progress(0, 100)

    # Per ADR-0013: Delegate to shared logic
    try:
        if ctx:
            await ctx.info("🎯 Creating buffers...")
            await ctx.report_progress(20, 100)

        # Call shared buffer logic
        result_data = vector.buffer(
            input_path=uri_path,
            output_path=str(output_path),
            distance=params.distance,
            resolution=params.resolution,
            ctx=ctx,
        )

        # Warn if geographic CRS
        if ctx and result_data.get("is_geographic"):
            await ctx.info(
                "⚠️  Geographic CRS detected. Buffer distance is in degrees. "
                "For metric buffers, reproject to projected CRS (e.g., UTM) first."
            )

        if ctx:
            await ctx.report_progress(90, 100)

        # Get output file size
        size_bytes = output_path.stat().st_size

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(
                f"✓ Buffering complete: {output_path} "
                f"({result_data['feature_count']} features, {size_bytes} bytes)"
            )

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver="auto",
            meta={
                "buffer_distance": params.distance,
                "resolution": params.resolution,
            },
        )

        # Return BufferResult
        return Result(
            output=resource_ref,
            feature_count=result_data["feature_count"],
            buffer_distance=result_data["buffer_distance"],
            resolution=result_data["resolution"],
            bounds=result_data.get("bounds"),
        )

    except ToolError:
        # Re-raise ToolError as-is
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error during vector buffering: {e}") from e


@mcp.tool(
    name="vector_buffer",
    description=(
        "Create buffer zones around vector geometries for proximity analysis. "
        "USE WHEN: Need to create zones of influence, analyze proximity, identify areas "
        "within distance of features, or create coverage areas. "
        "Common scenarios: Service area analysis (500m from transit stops), environmental "
        "buffers (wetland protection zones), proximity analysis (schools within 1km). "
        "REQUIRES: uri (source vector path), output (destination file path), "
        "distance (buffer distance in CRS units). "
        "OPTIONAL: resolution (segments per quadrant, 4-64, default 16). "
        "Higher resolution = smoother circles but slower performance. "
        "OUTPUT: VectorBufferResult with ResourceRef (output file URI/path/size/metadata), "
        "feature_count, buffer_distance applied, resolution used, bounds. "
        "SIDE EFFECTS: Creates new file at output path. Output geometry type is Polygon. "
        "SUPPORTS: Shapefile, GeoPackage, GeoJSON and other OGR formats. "
        "IMPORTANT: Distance in CRS units - meters for projected (UTM, State Plane), "
        "degrees for geographic (EPSG:4326). For metric buffers on lat/lon data, "
        "reproject to projected CRS first. Uses shapely for geometry operations. "
        "No reflection required - distance is user-specified."
    ),
)
async def buffer(
    uri: str,
    output: str,
    distance: float,
    resolution: int = 16,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for vector buffering with flattened parameters.

    No reflection middleware - buffer distance is explicitly user-directed.
    """
    # Build Params object from flattened parameters
    params = Params(
        distance=distance,
        resolution=resolution,
    )
    return await _buffer(uri, output, params, ctx)
