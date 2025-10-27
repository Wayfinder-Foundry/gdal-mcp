"""Vector clipping using pyogrio and shapely."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyogrio
import shapely
from fastmcp import Context
from fastmcp.exceptions import ToolError


def clip(
    input_path: str,
    output_path: str | Path,
    bounds: list[float] | None = None,
    mask: str | None = None,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Clip a vector dataset by bounding box or mask geometry.

    Args:
        input_path: Path to source vector dataset
        output_path: Path for output vector file
        bounds: Optional bounding box [minx, miny, maxx, maxy]
        mask: Optional path to mask geometry file
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary with clipping metadata:
        - feature_count: Number of features in output
        - geometry_type: Primary geometry type
        - bounds: Output spatial extent
        - clip_method: "bbox" or "mask"

    Raises:
        ToolError: If clipping fails or neither bounds nor mask provided
    """
    if bounds is None and mask is None:
        raise ToolError(
            "Either bounds or mask parameter required for clipping. "
            "Provide bounds=[minx, miny, maxx, maxy] or mask=<path_to_geometry>"
        )

    if bounds is not None and mask is not None:
        raise ToolError(
            "Cannot specify both bounds and mask. "
            "Use either bounds=[minx, miny, maxx, maxy] OR mask=<path>, not both."
        )

    try:
        # Read source data
        gdf = pyogrio.read_dataframe(input_path)

        if bounds is not None:
            # Clip by bounding box
            minx, miny, maxx, maxy = bounds
            bbox = shapely.box(minx, miny, maxx, maxy)

            # Clip geometries
            gdf_clipped = gdf[gdf.intersects(bbox)].copy()
            gdf_clipped["geometry"] = gdf_clipped.geometry.intersection(bbox)

            clip_method = "bbox"

        else:
            # Clip by mask geometry
            mask_gdf = pyogrio.read_dataframe(mask)

            # Union all mask geometries into single geometry
            mask_geom = mask_gdf.geometry.union_all()

            # Clip geometries
            gdf_clipped = gdf[gdf.intersects(mask_geom)].copy()
            gdf_clipped["geometry"] = gdf_clipped.geometry.intersection(mask_geom)

            clip_method = "mask"

        # Remove any empty geometries after clipping
        gdf_clipped = gdf_clipped[~gdf_clipped.geometry.is_empty]

        # Determine output driver from extension
        output_path_obj = Path(output_path)
        extension = output_path_obj.suffix.lower()
        driver_map = {
            ".shp": "ESRI Shapefile",
            ".gpkg": "GPKG",
            ".geojson": "GeoJSON",
            ".json": "GeoJSON",
        }
        driver = driver_map.get(extension, "GPKG")

        # Write clipped data
        pyogrio.write_dataframe(gdf_clipped, output_path, driver=driver)

        # Get output metadata
        output_info = pyogrio.read_info(str(output_path))

        # Extract bounds
        bounds_tuple = None
        if "total_bounds" in output_info and output_info["total_bounds"] is not None:
            b = output_info["total_bounds"]
            bounds_tuple = [float(b[0]), float(b[1]), float(b[2]), float(b[3])]

        return {
            "feature_count": len(gdf_clipped),
            "geometry_type": output_info.get("geometry_type"),
            "bounds": bounds_tuple,
            "clip_method": clip_method,
        }

    except Exception as e:
        if mask and ("cannot open" in str(e).lower() or "does not exist" in str(e).lower()):
            raise ToolError(
                f"Cannot open mask geometry at '{mask}'. "
                f"Ensure file exists and is a valid vector format. "
                f"Original error: {e}"
            ) from e
        elif "bounds" in str(e).lower():
            raise ToolError(
                f"Invalid bounds specification: {bounds}. "
                f"Bounds must be [minx, miny, maxx, maxy] with minx < maxx and miny < maxy. "
                f"Original error: {e}"
            ) from e
        else:
            raise ToolError(f"Vector clipping failed: {e}") from e
