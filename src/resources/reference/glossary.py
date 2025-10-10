"""Reference resource for geospatial glossary."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.reference import get_geospatial_glossary


@mcp.resource("reference://glossary/geospatial/{term}")
def list_geospatial_terms(
    term: str = "all",
    ctx: Context | None = None,
) -> dict:
    """Return glossary entries filtered by optional term substring."""
    normalized = None if not term or term.lower() == "all" else term
    entries = get_geospatial_glossary(normalized)
    if ctx and normalized:
        ctx.debug(f"Filtered glossary by term='{normalized}' -> {len(entries)} entries")
    return {"entries": entries, "total": len(entries)}
