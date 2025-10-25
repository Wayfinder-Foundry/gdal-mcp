"""CRS / datum justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts import Message, PromptMessage


def register(mcp: FastMCP) -> None:
    """Register CRS selection justification prompt."""

    @mcp.prompt(
        name="justify_crs_selection",
        description="Pre-execution micro-guidance for CRS/datum selection reasoning.",
        tags={"reasoning", "crs"},
    )
    def justify_crs_selection(dst_crs: str) -> list[PromptMessage]:
        """Justify target CRS selection for reprojection.

        Args:
            dst_crs: Target coordinate reference system (e.g., 'EPSG:3857')
        """
        content = (
            f"Before reprojecting to **{dst_crs}**:\n\n"
            "**Reason through:**\n"
            "• What spatial property must be preserved? "
            "(distance accuracy, area accuracy, shape, angular relationships)\n"
            "• Why is this CRS appropriate for the intended analysis?\n"
            "• What are the distortion characteristics and tradeoffs?\n"
            "• What alternative CRS options were considered and why were they rejected?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "property to preserve (e.g., area accuracy for land cover analysis)",\n'
            '  "alternatives": [\n'
            '    {"crs": "EPSG:XXXX", "why_not": "reason for rejection"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "crs": "{dst_crs}",\n'
            '    "rationale": "why this CRS fits the analytical intent",\n'
            '    "tradeoffs": "known distortions or limitations"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
