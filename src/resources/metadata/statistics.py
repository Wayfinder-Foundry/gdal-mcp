"""Metadata resource for raster statistics."""

from __future__ import annotations

from typing import Any

from src.app import mcp
from src.shared import raster


@mcp.resource("metadata://{file}/statistics")
def get_raster_statistics(file: str) -> dict[str, Any]:
    """Get lightweight raster statistics (read-only).

    Returns per-band statistics including min, max, mean, std, median, and
    percentiles (25/50/75). Histogram is disabled for lightweight planning
    use. This helps the AI choose methods and parameters during planning.
    """
    params = {"include_histogram": False, "percentiles": [25.0, 50.0, 75.0]}
    return raster.stats(file, params)
