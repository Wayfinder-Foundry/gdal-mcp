"""Tool for storing epistemic justifications."""

from __future__ import annotations

import logging

from fastmcp import Context

from src.app import mcp
from src.middleware.reflection_store import Justification, get_store
from src.middleware.reflection_transform import compute_reflection_hash

logger = logging.getLogger(__name__)


@mcp.tool(
    name="store_justification",
    description=(
        "Store an epistemic justification for later use. "
        "This tool is called after generating a methodological justification via a prompt. "
        "The stored justification allows subsequent tool calls to proceed "
        "without re-justification. "
        "REQUIRES: tool_name (name of the tool this justification is for), "
        "domain (crs_datum, resampling, hydrology, aggregation), "
        "prompt_name (name of the prompt that generated this), "
        "prompt_args (dict of arguments used in the prompt), "
        "justification (the generated justification as dict with "
        "intent/alternatives/choice/confidence). "
        "OUTPUT: Confirmation message with cache key."
    ),
)
async def store_justification(
    tool_name: str,
    domain: str,
    prompt_name: str,
    prompt_args: dict,
    justification: dict,
    ctx: Context | None = None,
) -> dict:
    """Store an epistemic justification in the reflection cache.

    Args:
        tool_name: Name of the tool this justification is for
        domain: Reflection domain (crs_datum, resampling, etc.)
        prompt_name: Name of the prompt that generated this justification
        prompt_args: Arguments that were passed to the prompt
        justification: The generated justification (structured data)
        ctx: Optional MCP context

    Returns:
        Confirmation with cache key and domain
    """
    # Compute hash from prompt arguments
    hash_key = compute_reflection_hash(tool_name, prompt_args, prompt_name, domain)

    # Validate and create Justification object
    validated = Justification.model_validate(justification)

    # Store in cache
    store = get_store()
    store.put(
        key=hash_key,
        value=validated,
        domain=domain,
    )

    if ctx:
        await ctx.info(
            f"✓ Stored justification for {prompt_name} in domain {domain} (hash={hash_key[:16]}...)"
        )

    logger.info(
        f"Stored justification: domain={domain}, prompt={prompt_name}, hash={hash_key[:16]}..."
    )

    return {
        "status": "stored",
        "domain": domain,
        "prompt_name": prompt_name,
        "cache_key": hash_key[:16] + "...",
        "message": "Justification stored. You can now retry the original tool call.",
    }
