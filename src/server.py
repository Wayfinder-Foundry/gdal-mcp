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
import src.tools.reflection.store_justification  # noqa: F401
import src.tools.vector.info  # noqa: F401

# ===============================================================
# prompts
# ===============================================================
from src.app import mcp
from src.middleware.reflection_middleware import ReflectionMiddleware
from src.prompts import register_prompts

# Register prompts (the epistemic layer)
register_prompts(mcp)

# ===============================================================
# reflection system
# ===============================================================

# Register reflection middleware
# This intercepts tool calls and checks for required justifications
mcp.add_middleware(ReflectionMiddleware())

__all__ = ["mcp"]
