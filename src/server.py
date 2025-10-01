"""
Compatibility module that exposes the shared FastMCP instance and ensures
all tool modules are imported so their @mcp.tool functions register.
"""
from __future__ import annotations


from gdal_mcp.app import mcp  # Shared FastMCP instance

# Import tool modules to register tools at import time
import gdal_mcp.tools  # package placeholder, keep for namespace
import gdal_mcp.tools.raster.info  # noqa: F401
import gdal_mcp.prompts  # noqa: F401
