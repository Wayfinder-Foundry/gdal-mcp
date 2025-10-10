"""
Server module that exposes the shared FastMCP instance and ensures
all tool modules are imported so their @mcp.tool functions register.
"""

from __future__ import annotations

# Import prompts
import src.prompts  # noqa: F401

# Import resource modules to register resources at import time
import src.resources.metadata.raster  # noqa: F401
import src.resources.metadata.statistics  # noqa: F401
import src.resources.metadata.vector  # noqa: F401
import src.tools.raster.convert  # noqa: F401

# Import tool modules to register tools at import time
import src.tools.raster.info  # noqa: F401
import src.tools.raster.reproject  # noqa: F401
import src.tools.raster.stats  # noqa: F401
import src.tools.vector.info  # noqa: F401
from src.app import mcp  # Shared FastMCP instance

__all__ = ["mcp"]
