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
# IMPORTANT: args_fn must extract ONLY the parameters that the corresponding prompt accepts
# to ensure cache keys match between middleware and stored justifications
TOOL_REFLECTIONS: dict[str, list[ReflectionSpec]] = {
    "raster_reproject": [
        ReflectionSpec(
            domain="crs_datum",
            prompt_name="justify_crs_selection",
            # justify_crs_selection(dst_crs: str) - only accepts dst_crs
            args_fn=lambda kwargs: {"dst_crs": kwargs.get("dst_crs", "unknown")},
        ),
        ReflectionSpec(
            domain="resampling",
            prompt_name="justify_resampling_method",
            # justify_resampling_method(method: str) - only accepts method
            args_fn=lambda kwargs: {"method": kwargs.get("resampling", "unknown")},
        ),
    ],
    "vector_reproject": [
        ReflectionSpec(
            domain="crs_datum",
            prompt_name="justify_crs_selection",
            # CRITICAL: Same domain and args as raster_reproject to enable
            # cross-domain cache sharing
            # justify_crs_selection(dst_crs: str) - only accepts dst_crs
            args_fn=lambda kwargs: {"dst_crs": kwargs.get("dst_crs", "unknown")},
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
