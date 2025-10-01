"""Configuration management for GDAL MCP server."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_workspaces_cache: list[Path] | None = None


def get_workspaces() -> list[Path]:
    """Load allowed workspace directories from environment variable.

    Reads GDAL_MCP_WORKSPACES environment variable (colon-separated paths).
    Configuration via fastmcp.json (FastMCP native):

        {
          "deployment": {
            "env": {
              "GDAL_MCP_WORKSPACES": "/data/projects:/home/user/gis"
            }
          }
        }

    Or via MCP client config (Claude Desktop, Cursor, etc.):

        {
          "mcpServers": {
            "gdal-mcp": {
              "command": "gdal-mcp",
              "env": {
                "GDAL_MCP_WORKSPACES": "/data/projects:/home/user/gis"
              }
            }
          }
        }

    Returns:
        List of allowed workspace directories (resolved to absolute paths).
        Empty list means no restrictions (all paths allowed).

    Examples:
        # Set via environment variable
        export GDAL_MCP_WORKSPACES="/data/projects:/home/user/gis"

        # Or in fastmcp.json
        {"deployment": {"env": {"GDAL_MCP_WORKSPACES": "/data:/home/user/gis"}}}
    """
    global _workspaces_cache

    # Return cached value if already loaded
    if _workspaces_cache is not None:
        return _workspaces_cache

    # Read from environment variable
    env_workspaces = os.getenv("GDAL_MCP_WORKSPACES")
    if env_workspaces:
        workspaces = [
            Path(ws.strip()).resolve() for ws in env_workspaces.split(":") if ws.strip()
        ]
        logger.info(
            f"✓ Loaded {len(workspaces)} workspace(s) from GDAL_MCP_WORKSPACES: "
            f"{', '.join(str(w) for w in workspaces)}"
        )
        _workspaces_cache = workspaces
        return workspaces

    # No configuration - allow all (with warning)
    logger.warning(
        "⚠️  No workspace configuration found. ALL PATHS ARE ALLOWED.\n"
        "   For production deployments, configure allowed workspaces:\n"
        "   \n"
        "   In fastmcp.json:\n"
        '     {"deployment": {"env": {"GDAL_MCP_WORKSPACES": "/data/projects:/home/user/gis"}}}\n'
        "   \n"
        "   Or in MCP client config:\n"
        '     {"mcpServers": {"gdal-mcp": {"env": {"GDAL_MCP_WORKSPACES": "/data:/home/gis"}}}}\n'
        "   \n"
        "   Or via shell:\n"
        '     export GDAL_MCP_WORKSPACES="/data/projects:/home/user/gis"\n'
        "   \n"
        "   See docs/ADR/0022-workspace-scoping-and-access-control.md for details."
    )
    _workspaces_cache = []
    return []


def reset_workspaces_cache() -> None:
    """Reset workspaces cache (useful for testing)."""
    global _workspaces_cache
    _workspaces_cache = None
