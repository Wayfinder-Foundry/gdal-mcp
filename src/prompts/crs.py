"""CRS / datum justification prompt."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.prompts import Message, PromptMessage


def register(mcp: FastMCP) -> None:
    """Register CRS selection justification prompt."""

    @mcp.prompt(
        name="justify_crs_selection",
        description="Advisory guidance for CRS/datum selection reasoning.",
        tags={"reasoning", "crs"},
    )
    def justify_crs_selection(dst_crs: str) -> list[PromptMessage]:
        """Guide reasoning about CRS selection for reprojection.

        This prompt helps document CRS choices and enables educational
        intervention when appropriate. The AI should:
        - Document reasoning for any CRS choice (user or AI-selected)
        - Ask the user conversationally if concerns are detected
        - Proceed with explicit user requirements without questioning

        Args:
            dst_crs: Target coordinate reference system (e.g., 'EPSG:3857')
        """
        content = (
            f"The operation will use **{dst_crs}** as the target coordinate system.\n\n"
            "**Your role:**\n"
            "• If the user explicitly specified this CRS: document why it's appropriate "
            "for their stated goal. If you see a potential issue they might not be aware of, "
            "ask them conversationally before proceeding.\n"
            "• If you're choosing this CRS autonomously: explain your reasoning.\n\n"
            "**Consider:**\n"
            "• What spatial property is most important? "
            "(distance accuracy, area accuracy, shape preservation, angular relationships)\n"
            "• Why is this CRS suitable for the intended use?\n"
            "• What are the distortion characteristics and acceptable tradeoffs?\n"
            "• If appropriate, what alternatives exist and why were they not chosen?\n\n"
            "**Provide structured reasoning:**\n"
            "```json\n"
            "{\n"
            f'  "crs": "{dst_crs}",\n'
            '  "intent": "property to preserve (e.g., area accuracy for land statistics)",\n'
            '  "rationale": "why this CRS achieves the intent",\n'
            '  "tradeoffs": "known distortions or limitations",\n'
            '  "user_advisory": "if concerns exist, note them here (optional)"\n'
            "}\n"
            "```\n\n"
            "If you have concerns about the user's choice, **ask them conversationally** "
            "before proceeding. Otherwise, document the reasoning and continue."
        )
        return [Message(content=content, role="user")]
