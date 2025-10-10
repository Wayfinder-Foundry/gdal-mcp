"""Vector metadata extraction using pyogrio or fiona."""

from __future__ import annotations

from typing import Any

import pyogrio
from fastmcp import Context
from fastmcp.exceptions import ToolError


def info(
    path: str,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Extract vector metadata using pyogrio (preferred) or fiona (fallback)."""
    try:
        vinfo = pyogrio.read_info(path)

        geometry_types: list[str] = []
        if vinfo.get("geometry_type"):
            geometry_types = [vinfo["geometry_type"]]

        fields: list[tuple[str, str]] = []
        if "fields" in vinfo:
            for field_name, field_type in zip(
                vinfo.get("fields", []), vinfo.get("dtypes", []), strict=False
            ):
                fields.append((str(field_name), str(field_type)))

        bounds_tuple = None
        if "total_bounds" in vinfo and vinfo["total_bounds"] is not None:
            b = vinfo["total_bounds"]
            bounds_tuple = (b[0], b[1], b[2], b[3])

        return {
            "path": path,
            "driver": vinfo.get("driver"),
            "crs": str(vinfo.get("crs")) if vinfo.get("crs") else None,
            "layer_count": 1,
            "geometry_types": geometry_types,
            "feature_count": int(vinfo.get("features", 0) or 0),
            "fields": fields,
            "bounds": bounds_tuple,
        }
    except Exception as e:
        msg = (
            f"Cannot open vector dataset at '{path}'. "
            "Ensure valid vector format (e.g., Shapefile, GPKG, GeoJSON)."
        )
        raise ToolError(msg) from e
