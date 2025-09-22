from __future__ import annotations

"""
Compatibility module that exposes the shared FastMCP instance and ensures
all tool modules are imported so their @mcp.tool functions register.
"""

from gdal_mcp.app import mcp  # Shared FastMCP instance

# Import tool packages to register tools at import time
import gdal_mcp.tools  # noqa: F401
import gdal_mcp.prompts  # noqa: F401
