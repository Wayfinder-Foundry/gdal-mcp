"""Configuration management for GDAL MCP server."""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_workspaces_cache: list[Path] | None = None


def _get_bool_env(var_name: str, *, default: bool = True) -> bool:
    """Read a boolean environment variable with strict, explicit values.

    Accepts only the following values (case-insensitive):
    - "1" or "true" → True
    - "0" or "false" → False

    Any other value logs a warning and returns the default to avoid
    surprising behavior.
    """
    raw_value = os.getenv(var_name)
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true"}:
        return True
    if normalized in {"0", "false"}:
        return False

    logger.warning(
        "Invalid value for %s: %s. Expected one of {1,true,0,false}. "
        "Falling back to default=%s.",
        var_name,
        raw_value,
        default,
    )
    return default


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
        workspaces = [Path(ws.strip()).resolve() for ws in env_workspaces.split(":") if ws.strip()]
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


def is_vector_tools_enabled() -> bool:
    """Return whether vector tools and resources should register."""
    return _get_bool_env("VECTOR", default=True)


def is_raster_tools_enabled() -> bool:
    """Return whether raster tools and resources should register."""
    return _get_bool_env("RASTER", default=True)


def get_workspace_root() -> Path | None:
    """Get the primary workspace root directory for resolving relative paths.

    Returns the first configured workspace, or None if no workspaces configured.
    This is used to resolve relative paths in tool calls to absolute paths.

    Returns:
        Primary workspace root as absolute Path, or None if unrestricted.
    """
    workspaces = get_workspaces()
    if workspaces:
        return workspaces[0]

    # No workspace configured - use current working directory
    cwd = Path.cwd()
    logger.debug(f"No workspace root configured, using CWD: {cwd}")
    return cwd


def resolve_path(path: str | Path) -> Path:
    """Resolve a path to absolute, using workspace root for relative paths.

    Args:
        path: Path string or Path object (can be relative or absolute)

    Returns:
        Absolute Path object

    Examples:
        >>> resolve_path("data/sample.tif")  # Relative
        Path("/workspace/data/sample.tif")

        >>> resolve_path("/absolute/path.tif")  # Absolute
        Path("/absolute/path.tif")
    """
    p = Path(path)

    if p.is_absolute():
        return p

    # Relative path - resolve against workspace root
    workspace_root = get_workspace_root()
    if workspace_root:
        resolved = (workspace_root / p).resolve()
        logger.debug(f"Resolved relative path '{path}' to '{resolved}'")
        return resolved

    # No workspace root - resolve against CWD
    return p.resolve()
