"""Decorator for automatic justification storage from prompts."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any

from src.middleware.reflection_store import Justification, get_store
from src.middleware.reflection_transform import compute_reflection_hash
from src.prompts.justification import Choice

logger = logging.getLogger(__name__)


def stores_justification(
    domain: str,
    prompt_name: str,
    tool_name: str,
) -> Callable[[Callable[..., Awaitable[str]]], Callable[..., Awaitable[str]]]:
    """Store prompt results as justifications automatically.

    NOTE: This decorator is currently unused because MCP prompts return templates,
    not generated justifications. The LLM generates justifications and must call
    the store_justification tool explicitly. This is kept for potential future use.

    Args:
        domain: Reflection domain (crs_datum, resampling, etc.)
        prompt_name: Name of the prompt (must match reflection config)
        tool_name: Name of the tool this justification is for

    Returns:
        Decorator function
    """

    def decorator(fn: Callable[..., Awaitable[str]]) -> Callable[..., Awaitable[str]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> str:
            # Call the original prompt function to generate justification
            justification_text = await fn(*args, **kwargs)

            # Compute hash from the prompt arguments
            hash_key = compute_reflection_hash(tool_name, kwargs, prompt_name, domain)

            # Store the justification in the cache
            store = get_store()
            justification = Justification(
                intent="Generated from prompt",
                alternatives=[],
                choice=Choice(method="auto", rationale=justification_text, tradeoffs=""),
                confidence="medium",
            )

            store.put(
                key=hash_key,
                value=justification,
                domain=domain,
            )

            logger.info(
                f"Stored justification for {prompt_name} in domain {domain} "
                f"(hash={hash_key[:16]}...)"
            )
            logger.debug(f"Justification content: {justification_text[:200]}...")

            # Return the justification text to the LLM
            return justification_text

        return wrapper

    return decorator
