from __future__ import annotations

import warnings

# Suppress Pydantic v1 deprecation warnings from FastMCP dependency
# TODO: Remove when FastMCP upgrades to Pydantic v2 model_config
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*Support for class-based `config` is deprecated.*",
)

from fastmcp import FastMCP

# Single FastMCP instance shared across tool modules
mcp = FastMCP("GDAL MCP", mask_error_details=True)
