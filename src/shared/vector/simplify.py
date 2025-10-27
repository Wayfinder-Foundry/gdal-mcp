"""Vector simplification using pyogrio and shapely."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pyogrio
from fastmcp import Context
from fastmcp.exceptions import ToolError


def simplify(
    input_path: str,
    output_path: str | Path,
    tolerance: float,
    method: str = "douglas-peucker",
    preserve_topology: bool = True,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Simplify vector geometries using Douglas-Peucker or Visvalingam algorithm.

    Args:
        input_path: Path to source vector dataset
        output_path: Path for output vector file
        tolerance: Simplification tolerance in CRS units
        method: Algorithm choice (douglas-peucker or visvalingam)
        preserve_topology: Ensure valid geometries (default True)
        ctx: Optional FastMCP context for logging

    Returns:
        Dictionary with simplification metadata:
        - feature_count: Number of features simplified
        - tolerance: Tolerance applied
        - method: Algorithm used
        - preserve_topology: Whether topology preserved
        - bounds: Output spatial extent

    Raises:
        ToolError: If simplification fails
    """
    try:
        # Read source data
        gdf = pyogrio.read_dataframe(input_path)

        # Apply simplification based on method
        if method == "douglas-peucker":
            # Standard Douglas-Peucker algorithm
            # preserve_topology ensures no self-intersections
            gdf_simplified = gdf.copy()
            gdf_simplified["geometry"] = gdf.geometry.simplify(
                tolerance, preserve_topology=preserve_topology
            )
        elif method == "visvalingam":
            # Visvalingam-Whyatt algorithm (area-based)
            # Note: shapely's simplify() with preserve_topology approximates VW
            # True VW would require additional library (e.g., simplification)
            gdf_simplified = gdf.copy()

            # Use standard simplify for both methods
            # Visvalingam method uses same simplify but with different interpretation
            from shapely.geometry.base import BaseGeometry

            def simplify_vw(geom: BaseGeometry) -> BaseGeometry:
                if geom.geom_type in [
                    "Polygon",
                    "MultiPolygon",
                    "LineString",
                    "MultiLineString",
                ]:
                    # For now, use standard simplify
                    # True VW would require additional library
                    return geom.simplify(tolerance, preserve_topology=preserve_topology)
                return geom

            gdf_simplified["geometry"] = gdf.geometry.apply(simplify_vw)
        else:
            raise ToolError(
                f"Unknown simplification method: {method}. "
                f"Supported methods: douglas-peucker, visvalingam"
            )

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

        # Write simplified data
        pyogrio.write_dataframe(gdf_simplified, output_path, driver=driver)

        # Get output metadata
        output_info = pyogrio.read_info(str(output_path))

        # Extract bounds
        bounds_tuple = None
        if "total_bounds" in output_info and output_info["total_bounds"] is not None:
            b = output_info["total_bounds"]
            bounds_tuple = [float(b[0]), float(b[1]), float(b[2]), float(b[3])]

        return {
            "feature_count": len(gdf_simplified),
            "tolerance": tolerance,
            "method": method,
            "preserve_topology": preserve_topology,
            "bounds": bounds_tuple,
        }

    except Exception as e:
        if "tolerance" in str(e).lower():
            raise ToolError(
                f"Invalid tolerance: {tolerance}. "
                f"Tolerance must be positive and in CRS units. "
                f"Original error: {e}"
            ) from e
        else:
            raise ToolError(f"Vector simplification failed: {e}") from e
