"""CRS / datum justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message


def register(mcp: FastMCP) -> None:
    """Register CRS selection justification prompt."""

    @mcp.prompt(
        name="justify_crs_selection",
        description="Pre-execution micro-guidance for CRS/datum selection reasoning.",
        tags={"reasoning", "crs"},
    )
    def justify_crs_selection(
        source_crs: str,
        target_crs: str,
        operation_context: str,
        data_type: str = "raster",
    ) -> list[Message]:
        content = (
            f"Before CRS transform **{source_crs}** → **{target_crs}** "
            f"({operation_context}):\n\n"
            "**Reason through:**\n"
            "• What property must stay truthful? "
            "(distance/area/shape/hydrology)\n"
            "• Datum shift risks? (vertical/horizontal alignment)\n"
            "• Distortion tradeoffs within analysis extent?\n"
            "• Why not other CRS options?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "property to preserve '
            '(e.g., distance accuracy for flow calculations)",\n'
            '  "alternatives": [\n'
            '    {"method": "EPSG:XXXX", "why_not": "reason for rejection"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "method": "{target_crs}",\n'
            '    "rationale": "why this CRS fits the intent",\n'
            '    "tradeoffs": "known distortions or limitations"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
