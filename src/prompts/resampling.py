"""Resampling method justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts import Message, PromptMessage


def register(mcp: FastMCP) -> None:
    """Register resampling justification prompt."""

    @mcp.prompt(
        name="justify_resampling_method",
        description="Advisory guidance for resampling method reasoning.",
        tags={"reasoning", "resampling"},
    )
    def justify_resampling_method(method: str) -> list[PromptMessage]:
        """Guide reasoning about resampling method selection.

        This prompt helps document resampling choices and enables educational
        intervention when appropriate. The AI should:
        - Document reasoning for any resampling choice (user or AI-selected)
        - Ask the user conversationally if concerns are detected
        - Proceed with explicit user requirements without questioning

        Args:
            method: Resampling method (e.g., 'cubic', 'nearest', 'bilinear')
        """
        content = (
            f"The operation will use **{method}** resampling.\n\n"
            "**Your role:**\n"
            "• If the user specified this method: document why it's appropriate for their data. "
            "If you see a concern (e.g., nearest for continuous data, cubic for categorical), "
            "ask them conversationally before proceeding.\n"
            "• If you're choosing this method: explain your reasoning.\n\n"
            "**Consider:**\n"
            "• What signal property must be preserved? "
            "(exact values, smooth gradients, class boundaries, statistical distribution)\n"
            "• Is the data categorical (discrete classes) or continuous (measurements)?\n"
            "• What artifacts or quality tradeoffs does this method introduce?\n"
            "• If appropriate, what alternatives exist and why weren't they chosen?\n\n"
            "**Common patterns:**\n"
            "• **nearest**: Categorical data, preserves exact values (creates blocky look)\n"
            "• **bilinear**: Continuous data, good balance of speed and quality\n"
            "• **cubic**: Continuous data, best quality (slower, smoothest)\n"
            "• **average**: Downsampling continuous data\n"
            "• **mode**: Downsampling categorical data\n\n"
            "**Provide structured reasoning:**\n"
            "```json\n"
            "{\n"
            f'  "method": "{method}",\n'
            '  "intent": "signal property to preserve (e.g., smooth gradients for elevation)",\n'
            '  "rationale": "why this method achieves the intent",\n'
            '  "tradeoffs": "artifacts or compromises",\n'
            '  "user_advisory": "if concerns exist, note them here (optional)"\n'
            "}\n"
            "```\n\n"
            "If you have concerns about the user's choice, **ask them conversationally** "
            "before proceeding. Otherwise, document the reasoning and continue."
        )
        return [Message(content=content, role="user")]
