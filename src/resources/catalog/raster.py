"""Catalog resource for raster datasets."""

from __future__ import annotations

from collections.abc import Iterable

from fastmcp import Context

from src.app import mcp

from .base import collect_entries


@mcp.resource("catalog://workspace/raster/{subpath}{?limit,include_hidden,extensions}")
def list_raster(
    subpath: str = "",
    limit: int | None = None,
    include_hidden: bool = False,
    extensions: Iterable[str] | None = None,
    ctx: Context | None = None,
) -> dict:
    """List raster-focused assets within configured workspaces."""
    response = collect_entries(
        ctx=ctx,
        kind="raster",
        limit=limit,
        include_hidden=include_hidden,
        extensions=list(extensions) if extensions is not None else None,
    )
    return response.to_dict()
