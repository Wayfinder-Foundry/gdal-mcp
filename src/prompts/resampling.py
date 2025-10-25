"""Resampling method justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts import Message, PromptMessage


def register(mcp: FastMCP) -> None:
    """Register resampling justification prompt."""

    @mcp.prompt(
        name="justify_resampling_method",
        description="Pre-execution micro-guidance for resampling method reasoning.",
        tags={"reasoning", "resampling"},
    )
    def justify_resampling_method(method: str) -> list[PromptMessage]:
        """Justify resampling method selection for reprojection.

        Args:
            method: Resampling method (e.g., 'cubic', 'nearest', 'bilinear')
        """
        content = (
            f"Before resampling using **{method}** method:\n\n"
            "**Reason through:**\n"
            "• What signal property must be preserved? "
            "(exact values, smooth gradients, class boundaries, statistical distribution)\n"
            "• Is the data categorical (discrete classes) or continuous (measurements)?\n"
            "• What artifacts or distortions might this method introduce?\n"
            "• What alternative resampling methods were considered and why were they rejected?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "signal property to preserve (e.g., exact class values for land cover)",\n'
            '  "alternatives": [\n'
            '    {"method": "nearest|bilinear|cubic|average|mode", "why_not": "reason"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "method": "{method}",\n'
            '    "rationale": "why this method preserves the signal property",\n'
            '    "tradeoffs": "artifacts or distortions introduced"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
