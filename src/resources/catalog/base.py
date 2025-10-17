"""Base catalog collection logic for workspace scanning."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from fastmcp import Context

from src.models.catalog import CatalogResponse
from src.shared.catalog import scan


def collect_entries(
    *,
    ctx: Context | None,
    kind: Literal["all", "raster", "vector"],
    limit: int | None = None,
    include_hidden: bool = False,
    extensions: Sequence[str] | None = None,
) -> CatalogResponse:
    """Collect and format catalog entries for a given dataset kind."""
    entries = scan(
        kind=kind,
        limit=limit,
        include_hidden=include_hidden,
        allowed_extensions=extensions,
        ctx=ctx,
    )
    return CatalogResponse(
        kind=None if kind == "all" else kind,
        entries=[entry.to_dict() for entry in entries],
        total=len(entries),
    )
