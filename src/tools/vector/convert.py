"""Vector format conversion tool using Python-native pyogrio."""

from __future__ import annotations

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.config import resolve_path
from src.models.resourceref import ResourceRef
from src.models.vector.convert import Params, Result
from src.shared import vector


async def _convert(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Convert a vector dataset to a different format.

    Args:
        uri: Path/URI to the source vector dataset (relative or absolute).
        output: Path for the output vector file (relative or absolute).
        params: Conversion parameters (driver, encoding).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the converted vector with ResourceRef.

    Raises:
        ToolError: If vector cannot be opened or conversion fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    if ctx:
        await ctx.info(f"📂 Opening source vector: {uri_path}")
        if params.driver:
            await ctx.debug(f"Target driver: {params.driver}")
        else:
            await ctx.debug(f"Auto-detecting driver from extension: {output_path.suffix}")
        await ctx.report_progress(0, 100)

    # Per ADR-0013: Delegate to shared logic
    try:
        if ctx:
            await ctx.info("🔄 Converting format...")
            await ctx.report_progress(20, 100)

        # Call shared conversion logic
        result_data = vector.convert(
            input_path=uri_path,
            output_path=str(output_path),
            driver=params.driver,
            encoding=params.encoding,
            ctx=ctx,
        )

        if ctx:
            await ctx.report_progress(90, 100)

        # Get output file size
        size_bytes = output_path.stat().st_size

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(
                f"✓ Conversion complete: {output_path} "
                f"({result_data['src_driver']} → {result_data['dst_driver']}, "
                f"{result_data['feature_count']} features, {size_bytes} bytes)"
            )

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver=result_data["dst_driver"],
            meta={
                "src_driver": result_data["src_driver"],
                "dst_driver": result_data["dst_driver"],
                "encoding": result_data["encoding"],
            },
        )

        # Return ConversionResult per ADR-0017
        return Result(
            output=resource_ref,
            src_driver=result_data["src_driver"],
            dst_driver=result_data["dst_driver"],
            feature_count=result_data["feature_count"],
            geometry_type=result_data.get("geometry_type"),
            encoding=result_data["encoding"],
        )

    except ToolError:
        # Re-raise ToolError as-is
        raise
    except Exception as e:
        raise ToolError(f"Unexpected error during vector conversion: {e}") from e


@mcp.tool(
    name="vector_convert",
    description=(
        "Convert vector dataset to different format with encoding control. "
        "USE WHEN: Need to migrate between formats (Shapefile ↔ GeoPackage ↔ GeoJSON), "
        "fix encoding issues, or prepare data for specific software requirements. "
        "Common scenarios: Shapefile to GeoPackage for single-file portability and UTF-8, "
        "GeoJSON to Shapefile for desktop GIS, GeoPackage to GeoJSON for web applications. "
        "REQUIRES: uri (source vector path), output (destination file path with extension). "
        "OPTIONAL: driver (auto-detected from extension: .shp, .gpkg, .geojson, .kml, .gml), "
        "encoding (UTF-8 default, ISO-8859-1 for legacy compatibility). "
        "OUTPUT: VectorConvertResult with ResourceRef (output file URI/path/size/metadata), "
        "src_driver, dst_driver, feature_count, geometry_type, encoding used. "
        "SIDE EFFECTS: Creates new file at output path. "
        "SUPPORTS: ESRI Shapefile, GeoPackage, GeoJSON, KML, GML and other OGR formats. "
        "NOTE: Uses pyogrio backend for performance. GeoPackage recommended for modern "
        "workflows (single file, UTF-8 native, no field name limits, efficient spatial indexing). "
        "No reflection required - format/compression choices covered by existing resources."
    ),
)
async def convert(
    uri: str,
    output: str,
    driver: str | None = None,
    encoding: str = "UTF-8",
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for vector format conversion with flattened parameters.

    No reflection middleware - format selection guidance available through
    reference resources (reference://formats/vector).
    """
    # Build Params object from flattened parameters
    params = Params(
        driver=driver,
        encoding=encoding,
    )
    return await _convert(uri, output, params, ctx)
