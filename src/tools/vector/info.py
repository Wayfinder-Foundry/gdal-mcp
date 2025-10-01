"""Vector info tool using Python-native pyogrio."""
from __future__ import annotations

try:
    import pyogrio  # noqa: F401
    HAS_PYOGRIO = True
except ImportError:
    HAS_PYOGRIO = False
    import fiona  # noqa: F401

from src.app import mcp
from src.models.vector import VectorInfo


async def get_vector_info(uri: str) -> VectorInfo:
    """Core logic: Return structured metadata for a vector dataset.

    Args:
        uri: Path/URI to the vector dataset (Shapefile, GeoPackage, GeoJSON, etc.).

    Returns:
        VectorInfo: Structured vector metadata with JSON schema.
    """
    if HAS_PYOGRIO:
        # Use pyogrio (faster, modern)
        return await _info_with_pyogrio(uri)
    else:
        # Fallback to fiona
        return await _info_with_fiona(uri)


async def _info_with_pyogrio(uri: str) -> VectorInfo:
    """Extract info using pyogrio."""
    import pyogrio
    
    # Read dataset info (metadata only, no features loaded)
    info = pyogrio.read_info(uri)
    
    # Extract geometry types from the dataset
    geometry_types = []
    if info.get("geometry_type"):
        geometry_types = [info["geometry_type"]]
    
    # Extract field schema
    fields = []
    if "fields" in info:
        for field_name, field_type in zip(info["fields"], info["dtypes"]):
            fields.append((field_name, str(field_type)))
    
    # Extract bounds (if available)
    bounds_tuple = None
    if "total_bounds" in info and info["total_bounds"] is not None:
        bounds_tuple = tuple(info["total_bounds"])
    
    # Build VectorInfo model
    return VectorInfo(
        path=uri,
        driver=info.get("driver"),
        crs=str(info["crs"]) if info.get("crs") else None,
        layer_count=1,  # pyogrio reads single layer at a time
        geometry_types=geometry_types,
        feature_count=info.get("features", 0),
        fields=fields,
        bounds=bounds_tuple,
    )


async def _info_with_fiona(uri: str) -> VectorInfo:
    """Extract info using fiona (fallback)."""
    import fiona
    
    with fiona.open(uri) as src:
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
        
        # Build VectorInfo model
        return VectorInfo(
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
    description="Inspect vector dataset metadata (CRS, geometry types, fields, bounds).",
)
async def vector_info(uri: str) -> VectorInfo:
    """MCP tool wrapper for vector info."""
    return await get_vector_info(uri)
