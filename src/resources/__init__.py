"""MCP Resources for GDAL operations.

Resources provide read-only information for AI planning:
- metadata: File properties and statistics
- catalog: Workspace discovery (future)
- reference: Domain knowledge (future)
- context: Session state (future)
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
