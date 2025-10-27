"""Preflight reflection decorator enforcing the private re-invocation flow."""

from __future__ import annotations

import hashlib
import inspect
import json
import logging
from collections.abc import Awaitable, Callable, Iterable
from functools import wraps
from typing import Any

from fastmcp.exceptions import ToolError

from src.middleware.reflection_store import get_store
from src.prompts import aggregation, crs, hydrology, resampling
from src.prompts.justification import Justification

logger = logging.getLogger(__name__)

MAX_REFLECTION_BYTES = 32 * 1024  # 32 KiB safety cap
ALLOWED_DOMAINS = {"crs_datum", "resampling", "hydrology", "aggregation"}
_TRANSIENT_ARG_TOKENS = ("path", "timestamp", "time", "tmp", "temp", "uuid", "nonce", "session")


_PROMPT_SOURCE_FETCHERS: dict[str, Callable[[], str]] = {
    "justify_crs_selection": lambda: inspect.getsource(crs.register),
    "justify_resampling_method": lambda: inspect.getsource(resampling.register),
    "justify_hydrology_conditioning": lambda: inspect.getsource(hydrology.register),
    "justify_aggregation_strategy": lambda: inspect.getsource(aggregation.register),
}


def _get_prompt_source(prompt_name: str) -> str:
    try:
        fetcher = _PROMPT_SOURCE_FETCHERS[prompt_name]
    except KeyError as exc:
        msg = f"Unknown prompt '{prompt_name}' configured for reflection preflight"
        raise ToolError(msg) from exc

    try:
        return fetcher()
    except (OSError, TypeError) as exc:
        raise ToolError(f"Unable to read prompt source for '{prompt_name}'") from exc


def _bind_arguments(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    signature = inspect.signature(fn)
    bound = signature.bind_partial(*args, **kwargs)
    bound.apply_defaults()
    return dict(bound.arguments)


def _normalize_value(value: Any, key_hint: str) -> Any:  # noqa: PLR0911
    key_lower = key_hint.lower()

    if value is None:
        return "unknown"

    if isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return "unknown"
        if "crs" in key_lower:
            return normalized.upper()
        if "method" in key_lower or "resampling" in key_lower:
            return normalized.lower()
        return normalized

    if isinstance(value, int | float | bool):
        return value

    if isinstance(value, dict):
        return {k: _normalize_value(v, f"{key_hint}.{k}") for k, v in sorted(value.items())}

    if isinstance(value, list | tuple | set):
        iterable: Iterable[Any]
        if isinstance(value, set):
            iterable = sorted(value)
        else:
            iterable = value
        return [_normalize_value(item, key_hint) for item in iterable]

    return str(value)


def _normalize_prompt_args(prompt_args: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in (prompt_args or {}).items():
        key_lower = key.lower()
        if any(token in key_lower for token in _TRANSIENT_ARG_TOKENS):
            continue
        normalized[key] = _normalize_value(value, key)
    return normalized


def _hash_prompt_content(prompt_name: str) -> str:
    prompt_source = _get_prompt_source(prompt_name)
    return hashlib.sha256(prompt_source.encode("utf-8")).hexdigest()[:16]


def _stable_hash(tool_name: str, prompt_args: dict[str, Any], domain: str, prompt_hash: str) -> str:
    """Compute stable hash for reflection cache lookup.

    NOTE: tool_name is NOT included in the hash payload to enable cross-domain
    cache sharing. A CRS justification for EPSG:3857 should be reusable across
    both raster_reproject and vector_reproject tools (same domain: crs_datum).

    The cache key is based on:
    - domain (e.g., crs_datum, resampling)
    - prompt_hash (ensures prompt hasn't changed)
    - prompt_args (e.g., dst_crs=EPSG:3857)

    This enables the architectural goal of domain-based (not tool-based) reflection.
    """
    payload = json.dumps(
        {
            "domain": domain,
            "prompt_hash": prompt_hash,
            **prompt_args,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(payload.encode()).hexdigest()}"


def _validate_and_persist_reflection(
    hash_key: str,
    domain: str,
    justification_data: dict[str, Any],
    tool_name: str,
) -> None:
    store = get_store()

    try:
        validated = Justification.model_validate(justification_data)
    except Exception as exc:  # pragma: no cover - pydantic handles details
        error_hints: list[dict[str, Any]] = []
        if hasattr(exc, "errors"):
            for err in exc.errors():
                field_path = ".".join(str(loc) for loc in err.get("loc", ()))
                error_hints.append(
                    {
                        "field": field_path,
                        "reason": err.get("msg", str(exc)),
                        "input": err.get("input"),
                    }
                )

        if error_hints:
            msg = (
                f"Invalid justification schema. Fix errors and re-invoke '{tool_name}' "
                "with corrected __reflection. "
                f"Errors: {error_hints}"
            )
            raise ToolError(msg) from exc
        raise ToolError(f"Invalid justification schema: {exc}") from exc

    store.put(hash_key, validated, domain)

    if validated.confidence == "low":
        logger.warning(
            "Low-confidence justification persisted for %s (domain=%s, hash=%s)",
            tool_name,
            domain,
            hash_key[:16],
        )
    else:
        logger.info(
            "Reflection persisted for %s (domain=%s, hash=%s)",
            tool_name,
            domain,
            hash_key[:16],
        )


def _build_spec_state(
    tool_name: str,
    spec: dict[str, Any],
    call_args: dict[str, Any],
) -> dict[str, Any]:
    args_fn = spec.get("args_fn")
    if not callable(args_fn):
        raise TypeError("Reflection spec args_fn must be callable")

    prompt_args_raw = args_fn(call_args) or {}
    if not isinstance(prompt_args_raw, dict):
        raise TypeError("Reflection args_fn must return a dict of prompt arguments")

    normalized_prompt_args = _normalize_prompt_args(prompt_args_raw)
    prompt_hash = _hash_prompt_content(spec["prompt_name"])
    hash_key = _stable_hash(tool_name, normalized_prompt_args, spec["domain"], prompt_hash)

    return {
        "spec": spec,
        "prompt_args": normalized_prompt_args,
        "hash_key": hash_key,
        "tool_name": tool_name,
    }


def requires_reflection(
    specs: dict[str, Any] | list[dict[str, Any]],
) -> Callable[[Callable[..., Any]], Callable[..., Awaitable[Any]]]:
    """Enforce the private reflection re-invocation flow via decorator."""
    spec_list = specs if isinstance(specs, list) else [specs]
    for spec in spec_list:
        if not all(key in spec for key in ("prompt_name", "domain", "args_fn")):
            raise ValueError("Each reflection spec must include: prompt_name, domain, args_fn")
        if spec["domain"] not in ALLOWED_DOMAINS:
            allowed = sorted(ALLOWED_DOMAINS)
            raise ValueError(
                f"Reflection spec domain '{spec['domain']}' is not in allowed domains {allowed}"
            )

    def decorator(fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            reflection_payload = kwargs.pop("__reflection", None)

            call_args = _bind_arguments(fn, *args, **kwargs)
            spec_states = [_build_spec_state(fn.__name__, spec, call_args) for spec in spec_list]

            if reflection_payload is not None:
                domain = reflection_payload.get("domain")
                provided_hash = reflection_payload.get("hash")
                justification = reflection_payload.get("justification")

                if not all([domain, provided_hash, justification]):
                    raise ToolError(
                        f"Invalid __reflection parameter for '{fn.__name__}'. "
                        "Must contain: hash, domain, justification"
                    )

                if domain not in ALLOWED_DOMAINS:
                    raise ToolError(
                        f"Invalid reflection domain '{domain}' provided to '{fn.__name__}'. "
                        f"Allowed domains: {sorted(ALLOWED_DOMAINS)}"
                    )

                matching_state = next(
                    (state for state in spec_states if state["spec"]["domain"] == domain),
                    None,
                )
                if matching_state is None:
                    raise ToolError(
                        f"Reflection domain '{domain}' is not required for '{fn.__name__}'."
                    )

                expected_hash = matching_state["hash_key"]
                if provided_hash != expected_hash:
                    raise ToolError(
                        "Reflection payload hash mismatch. "
                        "Re-run the prompt and re-invoke with the latest hint."
                    )

                serialized = json.dumps(justification, ensure_ascii=False)
                if len(serialized.encode("utf-8")) > MAX_REFLECTION_BYTES:
                    raise ToolError(
                        f"Reflection payload exceeds {MAX_REFLECTION_BYTES} bytes. "
                        "Shorten the justification and try again."
                    )

                _validate_and_persist_reflection(
                    hash_key=expected_hash,
                    domain=domain,
                    justification_data=justification,
                    tool_name=fn.__name__,
                )

            store = get_store()
            missing_specs: list[dict[str, Any]] = []
            for state in spec_states:
                spec = state["spec"]
                hash_key = state["hash_key"]
                if not store.has(hash_key, spec["domain"]):
                    missing_specs.append(
                        {
                            "spec": spec,
                            "prompt_args": state["prompt_args"],
                            "hash_key": hash_key,
                        }
                    )
                else:
                    logger.debug(
                        "Reflection cache hit for %s: %s (hash=%s)",
                        fn.__name__,
                        spec["domain"],
                        hash_key[:16],
                    )

            if missing_specs:
                first_missing = missing_specs[0]
                hint = {
                    "tool": fn.__name__,
                    "prompt": first_missing["spec"]["prompt_name"],
                    "prompt_args": first_missing["prompt_args"],
                    "hash": first_missing["hash_key"],
                    "domain": first_missing["spec"]["domain"],
                }
                if len(missing_specs) > 1:
                    hint["remaining_reflections"] = len(missing_specs) - 1

                message = (
                    f"Reflection required before executing '{fn.__name__}'. "
                    f"Call prompt '{hint['prompt']}', then re-invoke this tool "
                    "with __reflection parameter."
                )
                if len(missing_specs) > 1:
                    message += f"\n(Note: {len(missing_specs)} total reflections required)"

                raise ToolError(message + "\n\n" + json.dumps({"hint": hint}, indent=2))

            return await fn(*args, **kwargs)

        return wrapper

    return decorator


__all__ = [
    "requires_reflection",
    "_stable_hash",
    "_hash_prompt_content",
    "_normalize_prompt_args",
]
