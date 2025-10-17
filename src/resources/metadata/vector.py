"""Metadata resource for vector datasets."""

from __future__ import annotations

from typing import Any

from src.app import mcp
from src.shared import vector


@mcp.resource("metadata://{file}/vector")
def get_vector_metadata(file: str) -> dict[str, Any]:
    """Get vector spatial properties (read-only).

    Returns driver, CRS, bounds, geometry types, feature count, and field
    schema. Used by AI during planning to understand dataset properties
    and choose appropriate operations.
    """
    return vector.info(file)
