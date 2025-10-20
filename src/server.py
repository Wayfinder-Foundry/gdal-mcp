"""Server module that exposes the shared FastMCP instance.

Ensures all tool modules are imported so their @mcp.tool functions register.
"""

from __future__ import annotations

# ===============================================================
# resources/catalog
# ===============================================================
import src.resources.catalog.all  # noqa: F401
import src.resources.catalog.by_crs  # noqa: F401
import src.resources.catalog.raster  # noqa: F401
import src.resources.catalog.summary  # noqa: F401
import src.resources.catalog.vector  # noqa: F401

# ===============================================================
# resources/metadata
# ===============================================================
import src.resources.metadata.band  # noqa: F401
import src.resources.metadata.raster  # noqa: F401
import src.resources.metadata.statistics  # noqa: F401
import src.resources.metadata.vector  # noqa: F401
import src.tools.raster.convert  # noqa: F401

# ===============================================================
# tools
# ===============================================================
import src.tools.raster.info  # noqa: F401
import src.tools.raster.reproject  # noqa: F401
import src.tools.raster.stats  # noqa: F401
import src.tools.vector.info  # noqa: F401

# ===============================================================
# app
# ===============================================================
from src.app import mcp

__all__ = ["mcp"]
