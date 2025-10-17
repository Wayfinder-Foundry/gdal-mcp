"""Metadata resources for geospatial files.

Provides read-only access to file properties and statistics:
- raster: Raster metadata and statistics
- vector: Vector metadata
- format: Driver and format details
"""

from src.resources.metadata import format_detection, raster, vector

__all__ = ["format_detection", "raster", "vector"]
