"""Server module that exposes the shared FastMCP instance.

Ensures all tool modules are imported so their @mcp.tool functions register.
"""

from __future__ import annotations

# ===============================================================
# resources/catalog (always available)
# ===============================================================
import src.resources.catalog.all  # noqa: F401
import src.resources.catalog.by_crs  # noqa: F401
import src.resources.catalog.summary  # noqa: F401
from src.app import mcp
from src.config import is_raster_tools_enabled, is_vector_tools_enabled
from src.middleware.paths import PathValidationMiddleware
from src.middleware.reflection_middleware import ReflectionMiddleware
from src.prompts import register_prompts

if is_raster_tools_enabled():
    import src.resources.catalog.raster  # noqa: F401

if is_vector_tools_enabled():
    import src.resources.catalog.vector  # noqa: F401

# ===============================================================
# resources/metadata
# ===============================================================
if is_raster_tools_enabled():
    import src.resources.metadata.band  # noqa: F401
    import src.resources.metadata.raster  # noqa: F401
    import src.resources.metadata.statistics  # noqa: F401

if is_vector_tools_enabled():
    import src.resources.metadata.vector  # noqa: F401

# ===============================================================
# tools
# ===============================================================
if is_raster_tools_enabled():
    import src.tools.raster.convert  # noqa: F401
    import src.tools.raster.info  # noqa: F401
    import src.tools.raster.reproject  # noqa: F401
    import src.tools.raster.stats  # noqa: F401

if is_vector_tools_enabled():
    import src.tools.vector.buffer  # noqa: F401
    import src.tools.vector.clip  # noqa: F401
    import src.tools.vector.convert  # noqa: F401
    import src.tools.vector.info  # noqa: F401
    import src.tools.vector.reproject  # noqa: F401
    import src.tools.vector.simplify  # noqa: F401

import src.tools.reflection.store_justification  # noqa: F401

# ===============================================================
# prompts
# ===============================================================
# Register prompts (the epistemic layer)
register_prompts(mcp)

# ===============================================================
# reflection system
# ===============================================================

# Register path validation middleware (security layer)
# This enforces workspace boundaries and prevents directory traversal
mcp.add_middleware(PathValidationMiddleware())

# Register reflection middleware (epistemic layer)
# This intercepts tool calls and checks for required justifications
mcp.add_middleware(ReflectionMiddleware())

__all__ = ["mcp"]
