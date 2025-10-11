"""Metadata resource for per-band raster information."""

from __future__ import annotations

from typing import Any

from fastmcp import Context

from src.app import mcp
from src.shared.raster.bands import band_metadata


@mcp.resource("metadata://{file}/bands/{_dummy}")
def get_raster_band_metadata(
    file: str,
    _dummy: str = "info",
    include_statistics: bool = False,
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Return metadata for each band in a raster dataset.

    Args:
        file: Raster dataset path.
        _dummy: Placeholder segment to keep URI template consistent with FastMCP.
        include_statistics: Whether to compute approximate statistics for each band.
        ctx: Optional FastMCP context for logging.

    Returns:
        Dictionary containing band metadata.
    """
    if ctx:
        ctx.info(
            "[metadata://{file}/bands] Retrieving band metadata",
            extra={"file": file, "include_statistics": include_statistics},
        )

    return band_metadata(file, include_statistics=include_statistics)
