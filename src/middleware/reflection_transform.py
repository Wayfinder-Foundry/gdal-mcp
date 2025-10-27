"""Tool transformation for reflection preflight checks."""

from __future__ import annotations

import json
import logging
from typing import Any

from fastmcp.exceptions import ToolError

from src.middleware.preflight import (
    _hash_prompt_content,
    _normalize_prompt_args,
    _stable_hash,
)
from src.middleware.reflection_config import get_tool_reflections
from src.middleware.reflection_store import get_store

logger = logging.getLogger(__name__)


def compute_reflection_hash(
    tool_name: str,
    prompt_args: dict[str, Any],
    prompt_name: str,
    domain: str,
) -> str:
    """Compute hash for reflection cache lookup.

    Uses the same logic as the original preflight system.

    NOTE: tool_name parameter is kept for backwards compatibility but is NOT
    used in the hash computation. The hash is domain-based to enable cross-domain
    cache sharing (e.g., same CRS justification works for both raster and vector).

    Args:
        tool_name: Name of the tool being called (not used in hash, kept for API compat)
        prompt_args: Arguments that would be passed to the prompt
        prompt_name: Name of the prompt
        domain: Reflection domain

    Returns:
        SHA256 hash string
    """
    normalized = _normalize_prompt_args(prompt_args)
    prompt_hash = _hash_prompt_content(prompt_name)
    return _stable_hash(normalized, domain, prompt_hash)


async def reflection_preflight_check(
    tool_name: str,
    arguments: dict[str, Any],
) -> None:
    """Check if required reflections exist before allowing tool execution.

    This is registered as a FastMCP tool transformation. It runs before
    the actual tool function executes.

    Args:
        tool_name: Name of the tool being called
        arguments: Tool arguments (kwargs)

    Raises:
        ToolError: If required reflections are missing from cache
    """
    specs = get_tool_reflections(tool_name)
    if not specs:
        # No reflections required for this tool
        return

    store = get_store()
    missing_reflections: list[dict[str, Any]] = []

    for spec in specs:
        # Extract prompt arguments using the spec's args_fn
        prompt_args = spec.args_fn(arguments)

        # Compute hash for cache lookup
        hash_key = compute_reflection_hash(tool_name, prompt_args, spec.prompt_name, spec.domain)

        # Check if justification exists in cache
        if not store.has(hash_key, spec.domain):
            missing_reflections.append(
                {
                    "domain": spec.domain,
                    "prompt_name": spec.prompt_name,
                    "prompt_args": prompt_args,
                    "hash": hash_key,
                }
            )
            logger.info(
                f"Reflection cache miss for {tool_name}: {spec.domain} (hash={hash_key[:16]}...)"
            )
        else:
            logger.debug(
                f"Reflection cache hit for {tool_name}: {spec.domain} (hash={hash_key[:16]}...)"
            )

    if missing_reflections:
        # Build helpful error message
        first = missing_reflections[0]
        message = (
            f"⚠️  Epistemic preflight required for '{tool_name}'.\n\n"
            f"Before executing this operation, you must provide methodological justification.\n\n"
            f"**Required Action:**\n"
            f"1. Call the prompt '{first['prompt_name']}' with these arguments:\n"
            f"   {json.dumps(first['prompt_args'], indent=2)}\n\n"
            f"2. After the prompt completes, retry this tool call.\n"
        )

        if len(missing_reflections) > 1:
            message += f"\n**Note:** {len(missing_reflections)} total justifications required. "
            message += "They will be requested one at a time.\n"

        message += f"\n**Domain:** {first['domain']}"
        message += f"\n**Cache Key:** {first['hash'][:16]}..."

        raise ToolError(message)

    # All required reflections present - allow execution
    logger.info(f"All reflections present for {tool_name}, proceeding with execution")
