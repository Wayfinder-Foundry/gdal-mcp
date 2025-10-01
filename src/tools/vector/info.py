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


async def _info(
    uri: str,
    ctx: Context | None = None,
) -> Info:
    """Core logic: Return structured metadata for a vector dataset.

    Args:
        uri: Path/URI to the vector dataset (Shapefile, GeoPackage, GeoJSON, etc.).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Info: Structured vector metadata with JSON schema.
    
    Raises:
        ToolError: If vector dataset cannot be opened.
    """
    if ctx:
        await ctx.info(f"📂 Opening vector dataset: {uri}")
    
    try:
        if HAS_PYOGRIO:
            if ctx:
                await ctx.debug("Using pyogrio backend")
            return await _info_with_pyogrio(uri, ctx)
        else:
            if ctx:
                await ctx.debug("Using fiona backend (pyogrio not available)")
            return await _info_with_fiona(uri, ctx)
    
    except Exception as e:
        # Catch any backend-specific errors and convert to ToolError
        raise ToolError(
            f"Cannot open vector dataset at '{uri}'. "
            f"Please ensure: (1) file exists, (2) file is a valid vector format. "
            f"Supported formats: Shapefile (.shp), GeoPackage (.gpkg), "
            f"GeoJSON (.geojson/.json), KML (.kml), CSV (.csv with geometry), "
            f"and other OGR-supported formats. "
            f"Original error: {str(e)}"
        ) from e


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
        for field_name, field_type in zip(vinfo["fields"], vinfo["dtypes"]):
            fields.append((field_name, str(field_type)))
    
    # Extract bounds (if available)
    bounds_tuple = None
    if "total_bounds" in vinfo and vinfo["total_bounds"] is not None:
        bounds_tuple = tuple(vinfo["total_bounds"])
    
    if ctx:
        await ctx.info(
            f"✓ Metadata extracted: {len(fields)} fields, "
            f"{vinfo.get('features', 0)} features"
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
            await ctx.debug(
                f"✓ Driver: {src.driver}, Features: {len(src)}, CRS: {src.crs}"
            )
        
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
            await ctx.info(
                f"✓ Metadata extracted: {len(fields)} fields, {len(src)} features"
            )
        
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
    name="vector.info",
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
