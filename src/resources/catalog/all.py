"""Catalog resource for all workspace datasets."""

from __future__ import annotations

from collections.abc import Iterable

from fastmcp import Context

from src.app import mcp

from .base import collect_entries


@mcp.resource("catalog://workspace/all/{subpath}{?limit,include_hidden,extensions}")
def list_all(
    subpath: str = "",
    limit: int | None = None,
    include_hidden: bool = False,
    extensions: Iterable[str] | None = None,
    ctx: Context | None = None,
) -> dict:
    """List all catalogued workspace assets.

    Args:
        subpath: Optional relative subdirectory to scope results ("" = root).
        limit: Maximum number of entries to return (None = unlimited).
        include_hidden: Include hidden files and directories when True.
        extensions: Optional extension whitelist (e.g. `["tif", "gpkg"]`).
        ctx: Optional FastMCP context for boundary logging.
    """
    response = collect_entries(
        ctx=ctx,
        kind="all",
        limit=limit,
        include_hidden=include_hidden,
        extensions=list(extensions) if extensions is not None else None,
    )
    return response.to_dict()
