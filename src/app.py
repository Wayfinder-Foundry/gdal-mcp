from __future__ import annotations

import warnings

from fastmcp import FastMCP

from src.middleware import PathValidationMiddleware

GLOBAL_INSTRUCTIONS = (
    "You are the GDAL MCP geospatial analysis agent."
    " Always reason in domain language before invoking tools."
    " Prefer discovering context via resources (catalog://, metadata://, reference://)"
    " before running tools, and explicitly validate results with quality checks."
    " Ask for clarification when data is missing or ambiguous, propose step-by-step"
    " workflows with rationale, and wait for user confirmation before executing"
    " expensive multi-step pipelines."
)

# Suppress Pydantic v1 deprecation warnings from FastMCP dependency
# TODO: Remove when FastMCP upgrades to Pydantic v2 model_config
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*Support for class-based `config` is deprecated.*",
)

# Single FastMCP instance shared across tool modules
mcp = FastMCP(
    "GDAL MCP",
    instructions=GLOBAL_INSTRUCTIONS,
    mask_error_details=True,
)

# Add path validation middleware for workspace scoping (ADR-0022)
# This automatically validates all file paths against allowed workspaces
mcp.add_middleware(PathValidationMiddleware())
