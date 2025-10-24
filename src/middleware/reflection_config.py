"""Reflection configuration mapping tools to required justifications."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

# Type for args_fn that extracts prompt arguments from tool kwargs
ArgsExtractor = Callable[[dict[str, Any]], dict[str, Any]]


class ReflectionSpec:
    """Specification for a required reflection/justification."""

    def __init__(
        self,
        domain: str,
        prompt_name: str,
        args_fn: ArgsExtractor,
    ):
        """Initialize reflection spec.

        Args:
            domain: Reflection domain (crs_datum, resampling, etc.)
            prompt_name: Name of the prompt to call for justification
            args_fn: Function to extract prompt args from tool kwargs
        """
        self.domain = domain
        self.prompt_name = prompt_name
        self.args_fn = args_fn


# Configuration mapping tool names to their reflection requirements
TOOL_REFLECTIONS: dict[str, list[ReflectionSpec]] = {
    "raster_reproject": [
        ReflectionSpec(
            domain="crs_datum",
            prompt_name="justify_crs_selection",
            args_fn=lambda kwargs: {
                "source_crs": kwargs.get("src_crs") or "source CRS",
                "target_crs": kwargs.get("dst_crs", "unknown"),
                "operation_context": "raster reprojection",
                "data_type": "raster",
            },
        ),
        ReflectionSpec(
            domain="resampling",
            prompt_name="justify_resampling_method",
            args_fn=lambda kwargs: {
                "data_type": "raster",
                "source_resolution": "original",
                "target_resolution": "resampled",
                "method": kwargs.get("resampling", "unknown"),
                "operation_context": "reprojection resampling",
            },
        ),
    ],
}


def get_tool_reflections(tool_name: str) -> list[ReflectionSpec]:
    """Get reflection specs for a tool.

    Args:
        tool_name: Name of the tool

    Returns:
        List of reflection specs, empty if tool has no reflections
    """
    return TOOL_REFLECTIONS.get(tool_name, [])


def has_reflections(tool_name: str) -> bool:
    """Check if a tool requires reflections.

    Args:
        tool_name: Name of the tool

    Returns:
        True if tool has reflection requirements
    """
    return tool_name in TOOL_REFLECTIONS
