"""Aggregation strategy justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts import Message, PromptMessage


def register(mcp: FastMCP) -> None:
    """Register aggregation justification prompt."""

    @mcp.prompt(
        name="justify_aggregation_strategy",
        description="Pre-execution micro-guidance for aggregation/statistical reasoning.",
        tags={"reasoning", "aggregation"},
    )
    def justify_aggregation_strategy(
        aggregation_type: str,
        statistic: str,
        zones: str | None = None,
        operation_context: str | None = None,
    ) -> list[PromptMessage]:
        extras = []
        if zones:
            extras.append(f"Zones: {zones}")
        if operation_context:
            extras.append(operation_context)
        context_suffix = f" ({', '.join(extras)})" if extras else ""

        content = (
            f"Before aggregation **{aggregation_type}** using **{statistic}**"
            f"{context_suffix}:\n\n"
            "**Reason through:**\n"
            "• Interpretation goal? (central tendency/dominance/extremes)\n"
            "• How does statistic preserve phenomenon?\n"
            "• Distribution/independence/zone design assumptions?\n"
            "• Why not mean/median/mode/sum/min/max?\n\n"
            "**Return strict JSON:**\n"
            "```json\n"
            "{\n"
            '  "intent": "interpretation goal (e.g., typical value, dominant class)",\n'
            '  "alternatives": [\n'
            '    {"method": "mean|median|mode|sum|min|max", "why_not": "reason"}\n'
            "  ],\n"
            '  "choice": {\n'
            f'    "method": "{statistic}",\n'
            '    "rationale": "why this statistic captures the intent",\n'
            '    "tradeoffs": "information lost or de-emphasized"\n'
            "  },\n"
            '  "confidence": "low|medium|high"\n'
            "}\n"
            "```"
        )
        return [Message(content=content, role="user")]
