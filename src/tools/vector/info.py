"""Vector info tool using Python-native pyogrio."""

from __future__ import annotations

try:
    import pyogrio  # noqa: F401

    HAS_PYOGRIO = True
except ImportError:
    HAS_PYOGRIO = False
    import fiona  # noqa: F401

from fastmcp import Context
from fastmcp.exceptions import ToolError

from src.app import mcp
from src.models.vector.info import Info
from src.shared import vector


async def _info(
    uri: str,
    ctx: Context | None = None,
) -> Info:
    """Return structured metadata for a vector dataset using shared extractor."""
    try:
        data = vector.info(uri, ctx)
        return Info(
            path=data["path"],
            driver=data.get("driver"),
            crs=data.get("crs"),
            layer_count=data.get("layer_count"),
            geometry_types=list(data.get("geometry_types", [])),
            feature_count=data.get("feature_count"),
            fields=[(str(n), str(t)) for n, t in data.get("fields", [])],
            bounds=tuple(data["bounds"]) if data.get("bounds") is not None else None,
        )
    except Exception as e:
        message = (
            f"Cannot open vector dataset at '{uri}'. "
            "Ensure the file exists and is a supported vector format."
        )
        raise ToolError(message) from e


async def _info_with_pyogrio(uri: str, ctx: Context | None = None) -> Info:
    """Extract info using pyogrio."""
    import pyogrio

    # Read dataset info (metadata only, no features loaded)
    vinfo = pyogrio.read_info(uri)

    if ctx:
        await ctx.debug(
            f"✓ Driver: {vinfo.get('driver')}, Features: {vinfo.get('features', 0)}, "
            f"CRS: {vinfo.get('crs')}"
        )

    # Extract geometry types from the dataset
    geometry_types = []
    if vinfo.get("geometry_type"):
        geometry_types = [vinfo["geometry_type"]]

    # Extract field schema
    fields = []
    if "fields" in vinfo:
        for field_name, field_type in zip(vinfo["fields"], vinfo["dtypes"], strict=False):
            fields.append((field_name, str(field_type)))

    # Extract bounds (if available)
    bounds_tuple = None
    if "total_bounds" in vinfo and vinfo["total_bounds"] is not None:
        bounds_tuple = tuple(vinfo["total_bounds"])

    if ctx:
        await ctx.info(
            f"✓ Metadata extracted: {len(fields)} fields, {vinfo.get('features', 0)} features"
        )

    # Build VectorInfo model
    return Info(
        path=uri,
        driver=vinfo.get("driver"),
        crs=str(vinfo["crs"]) if vinfo.get("crs") else None,
        layer_count=1,  # pyogrio reads single layer at a time
        geometry_types=geometry_types,
        feature_count=vinfo.get("features", 0),
        fields=fields,
        bounds=bounds_tuple,
    )


async def _info_with_fiona(uri: str, ctx: Context | None = None) -> Info:
    """Extract info using fiona (fallback)."""
    import fiona

    with fiona.open(uri) as src:
        if ctx:
            await ctx.debug(f"✓ Driver: {src.driver}, Features: {len(src)}, CRS: {src.crs}")

        # Extract geometry type
        geometry_types = []
        if src.schema.get("geometry"):
            geometry_types = [src.schema["geometry"]]

        # Extract field schema
        fields = []
        if "properties" in src.schema:
            for field_name, field_type in src.schema["properties"].items():
                fields.append((field_name, field_type))

        # Extract bounds
        bounds_tuple = None
        if src.bounds:
            bounds_tuple = src.bounds

        if ctx:
            await ctx.info(f"✓ Metadata extracted: {len(fields)} fields, {len(src)} features")

        # Build VectorInfo model
        return Info(
            path=uri,
            driver=src.driver,
            crs=str(src.crs) if src.crs else None,
            layer_count=1,  # Single layer per fiona dataset
            geometry_types=geometry_types,
            feature_count=len(src),
            fields=fields,
            bounds=bounds_tuple,
        )


@mcp.tool(
    name="vector_info",
    description=(
        "Inspect vector dataset metadata using Python-native pyogrio (or fiona fallback). "
        "USE WHEN: Need to understand vector dataset properties before processing, "
        "verify CRS and spatial extent, check geometry types (Point, LineString, Polygon), "
        "examine attribute fields and types, or validate feature count. "
        "Common scenarios: verify Shapefile structure, check GeoJSON CRS, "
        "inspect GeoPackage layers, or validate CSV with geometry. "
        "REQUIRES: uri (path to vector file or dataset). "
        "OPTIONAL: None. "
        "OUTPUT: VectorInfo with path, driver (e.g. 'ESRI Shapefile', 'GeoJSON', 'GPKG'), "
        "crs (e.g. 'EPSG:4326'), layer_count (number of layers), "
        "geometry_types (list like ['Point', 'MultiPolygon']), "
        "feature_count (number of features/records), "
        "fields (list of tuples with field name and type like [('name', 'str'), ('pop', 'int')]), "
        "bounds (spatial extent as (minx, miny, maxx, maxy) or None). "
        "SIDE EFFECTS: None (read-only operation, metadata only - features not loaded). "
        "NOTE: Uses pyogrio backend for performance (falls back to fiona if unavailable). "
        "Both backends support Shapefile, GeoPackage, GeoJSON, KML, and other OGR formats."
    ),
)
async def info(
    uri: str,
    ctx: Context | None = None,
) -> Info:
    """MCP tool wrapper for vector info."""
    return await _info(uri, ctx)
