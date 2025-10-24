from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP(name="GDAL-MCP")

mcp.system_prompt = (
    "You are governed by epistemic responsibility. When an operation touches "
    "CRS/Datum, Resampling, Hydrology Conditioning, or Aggregation (interpretation), "
    "you must run epistemic preflight and produce a justification object if methodology "
    "must be surfaced. Provide JSON only."
)
