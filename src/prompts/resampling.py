"""Resampling method justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message


def register(mcp: FastMCP) -> None:
    """Register resampling justification prompt."""

    @mcp.prompt(
        name="justify_resampling_method",
        description="Pre-execution micro-guidance for resampling method reasoning.",
        tags={"reasoning", "resampling"},
    )
    def justify_resampling_method(
        data_type: str,
        source_resolution: str,
        target_resolution: str,
        method: str,
        operation_context: str,
    ) -> list[Message]:
        content = (
            f"Before resampling **{data_type}** from {source_resolution} → "
            f"{target_resolution} using **{method}** ({operation_context}):\n\n"
            "**Reason through:**\n"
            "• Signal property to preserve? "
            "(class fidelity/gradient/distribution)\n"
            "• Categorical vs continuous implications?\n"
            "• Artifact risks? (smoothing/aliasing/false classes)\n"
            "• Why not nearest/bilinear/cubic/mode/average?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "signal property to preserve '
            '(e.g., classification fidelity)",\n'
            '  "alternatives": [\n'
            '    {"method": "nearest|bilinear|cubic|mode|average", '
            '"why_not": "reason"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "method": "{method}",\n'
            '    "rationale": "why this method preserves the intent",\n'
            '    "tradeoffs": "artifacts introduced (e.g., smoothing)"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
