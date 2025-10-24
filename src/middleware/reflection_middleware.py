"""FastMCP middleware for reflection preflight checks."""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.middleware.middleware import CallNext, Middleware, MiddlewareContext

from src.middleware.reflection_transform import reflection_preflight_check

logger = logging.getLogger(__name__)


class ReflectionMiddleware(Middleware):
    """Middleware that performs reflection preflight checks before tool execution.

    This middleware intercepts tool calls and checks if required epistemic
    justifications exist in the cache. If not, it raises a ToolError that
    instructs the LLM to call the appropriate prompt first.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        """Intercept tool calls to perform reflection preflight check.

        Args:
            context: Middleware context with request details
            call_next: Next handler in the chain

        Returns:
            Result from the tool or raises ToolError if reflections missing
        """
        # Extract tool name and arguments from context (support both new and legacy APIs)
        tool_name = None
        arguments: dict[str, Any] = {}
        try:
            # Preferred FastMCP API
            tool_name = context.message.name
            arguments = context.message.arguments or {}
        except AttributeError:
            # Fallback to legacy request-based API if present
            request = getattr(context, "request", None)
            if request is not None and hasattr(request, "params"):
                params = request.params or {}
                tool_name = params.get("name")
                arguments = params.get("arguments", {}) or {}

        logger.debug(f"Reflection middleware intercepting tool call: {tool_name}")

        # If we cannot determine the tool name, skip preflight to avoid hard failure
        if not tool_name:
            logger.warning(
                "ReflectionMiddleware: Unable to determine tool name; skipping preflight"
            )
            return await call_next(context)

        # Perform preflight check
        # This will raise ToolError if justifications are missing
        await reflection_preflight_check(tool_name, arguments)

        # All reflections present, proceed with tool execution
        return await call_next(context)
