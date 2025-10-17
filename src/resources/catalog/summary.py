"""Workspace summary catalog resource."""

from __future__ import annotations

from fastmcp import Context

from src.app import mcp
from src.shared.catalog.summary import generate_workspace_summary


@mcp.resource("catalog://workspace/summary/{_dummy}")
def get_workspace_summary(_dummy: str = "overview", ctx: Context | None = None) -> dict:
    """Provide a high-level summary of all configured workspaces.

    Returns counts by dataset type, CRS distribution, format distribution,
    and size statistics to help AI understand workspace contents at a glance.

    This resource is ideal for:
    - Initial workspace exploration
    - Understanding data diversity (formats, projections)
    - Planning batch operations across similar datasets
    - Identifying dominant CRS for workflow alignment

    Args:
        _dummy: Placeholder parameter (use 'overview' or any value)
        ctx: Optional context for logging
    """
    if ctx:
        ctx.info("[catalog://workspace/summary] Generating workspace summary")

    summary = generate_workspace_summary(ctx=ctx)
    return summary.model_dump()
