"""Prompt registration for GDAL-MCP server."""

from __future__ import annotations

from fastmcp import FastMCP

from . import aggregation, crs, hydrology, resampling

__all__ = ["register_prompts"]


def register_prompts(mcp: FastMCP) -> None:
    """Register prompt templates with the FastMCP server.

    Registers epistemic guidance prompts that provide structured
    justification templates for risky geospatial operations.
    """

    crs.register(mcp)
    resampling.register(mcp)
    hydrology.register(mcp)
    aggregation.register(mcp)
