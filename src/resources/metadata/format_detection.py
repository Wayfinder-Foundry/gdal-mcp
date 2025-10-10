"""Metadata resource for dataset format information."""

from __future__ import annotations

from typing import Any

from fastmcp.exceptions import ToolError

from src.app import mcp
from src.shared.metadata.format_detection import read_format_metadata


@mcp.resource("metadata://{file}/format")
def get_format_metadata(file: str) -> dict[str, Any]:
    """Return driver and format characteristics for a dataset."""
    try:
        return read_format_metadata(file)
    except FileNotFoundError as exc:
        raise ToolError(f"File not found: {file}") from exc
