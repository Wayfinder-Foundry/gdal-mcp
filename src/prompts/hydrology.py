"""Hydrology conditioning justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message


def register(mcp: FastMCP) -> None:
    """Register hydrology conditioning justification prompt."""

    @mcp.prompt(
        name="justify_hydrology_conditioning",
        description="Pre-execution micro-guidance for hydrologic conditioning reasoning.",
        tags={"reasoning", "hydrology"},
    )
    def justify_hydrology_conditioning(
        conditioning_method: str,
        intent: str,
        watershed_extent: str | None = None,
        data_resolution: str | None = None,
    ) -> list[Message]:
        extras = []
        if watershed_extent:
            extras.append(f"Extent: {watershed_extent}")
        if data_resolution:
            extras.append(f"Resolution: {data_resolution}")
        context_suffix = f" ({', '.join(extras)})" if extras else ""

        content = (
            f"Before hydrologic conditioning using **{conditioning_method}** "
            f"for {intent}{context_suffix}:\n\n"
            "**Reason through:**\n"
            "• Hydrologic property to preserve? "
            "(flow paths/accumulation/sinks)\n"
            "• Why fill/breach/burn/snap for this basin?\n"
            "• DEM quality/sink/stream alignment assumptions?\n"
            "• Why not other conditioning strategies?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "hydrologic property to preserve '
            '(e.g., natural flow connectivity)",\n'
            '  "alternatives": [\n'
            '    {"method": "fill|breach|burn|snap", "why_not": "reason"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "method": "{conditioning_method}",\n'
            '    "rationale": "how this preserves hydrologic behavior",\n'
            '    "tradeoffs": "compromises (e.g., flattening depressions)"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
