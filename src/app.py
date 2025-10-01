from __future__ import annotations

from fastmcp import FastMCP

# Single FastMCP instance shared across tool modules
mcp = FastMCP("gdal-mcp", mask_error_details=True)
