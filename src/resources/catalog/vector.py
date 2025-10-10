"""Catalog resource for vector datasets."""

from __future__ import annotations

from collections.abc import Iterable

from fastmcp import Context

from src.app import mcp

from .base import collect_entries


@mcp.resource("catalog://workspace/vector/{subpath}{?limit,include_hidden,extensions}")
def list_vector(
    subpath: str = "",
    limit: int | None = None,
    include_hidden: bool = False,
    extensions: Iterable[str] | None = None,
    ctx: Context | None = None,
) -> dict:
    """List vector-focused assets within configured workspaces."""
    response = collect_entries(
        ctx=ctx,
        kind="vector",
        limit=limit,
        include_hidden=include_hidden,
        extensions=list(extensions) if extensions is not None else None,
    )
    return response.to_dict()
