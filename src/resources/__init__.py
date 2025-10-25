"""MCP Resources for GDAL operations.

Resources provide read-only information per ADR-0023:
- metadata://  File properties and statistics
- catalog://   Workspace discovery
- reference:// System capabilities (formats, CRS, compression, glossary)
"""

from src.resources import catalog, reference
from src.resources.metadata import band, format_detection, raster, statistics, vector

__all__ = [
    "catalog",
    "reference",
    "band",
    "format_detection",
    "raster",
    "vector",
    "statistics",
]
