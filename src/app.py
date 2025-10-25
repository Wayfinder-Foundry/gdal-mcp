from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP(
    name="GDAL-MCP",
    instructions=(
        "GDAL-MCP provides geospatial data processing tools, resources, and methodology "
        "guidance. You have access to: (1) Tools for raster/vector operations "
        "(reproject, convert, info, stats), (2) Resources for discovering workspace data, "
        "file metadata, and reference knowledge (CRS, compression, resampling methods), "
        "(3) Prompts for epistemic reasoning when scientific correctness requires "
        "methodological justification. Operations touching CRS/datum, resampling, hydrology "
        "conditioning, or aggregation may trigger epistemic preflight to ensure scientific "
        "validity."
    ),
)
