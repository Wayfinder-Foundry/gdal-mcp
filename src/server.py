"""
Server module that exposes the shared FastMCP instance and ensures
all tool modules are imported so their @mcp.tool functions register.
"""
from __future__ import annotations

from src.app import mcp  # Shared FastMCP instance

# Import tool modules to register tools at import time
import src.tools.raster.info  # noqa: F401
import src.tools.raster.convert  # noqa: F401
import src.tools.raster.reproject  # noqa: F401
import src.tools.raster.stats  # noqa: F401
import src.tools.vector.info  # noqa: F401

# Import prompts
import src.prompts  # noqa: F401

__all__ = ["mcp"]
