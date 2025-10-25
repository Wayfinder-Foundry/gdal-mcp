"""Epistemic risk classification and hashing utilities."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from enum import Enum, auto
from typing import Any

RelevantArgs = Mapping[str, Any]


class RiskClass(Enum):
    """Enumerates epistemic risk classes that require justification."""

    NONE = auto()
    CRS_DATUM = auto()
    RESAMPLING = auto()
    HYDROLOGY = auto()
    AGGREGATION = auto()


# Keywords used to infer risk from tool names
_TOOL_KEYWORDS: dict[RiskClass, tuple[str, ...]] = {
    RiskClass.CRS_DATUM: (
        "reproject",
        "transform",
        "warp",
        "datum",
        "crs",
    ),
    RiskClass.RESAMPLING: (
        "resample",
        "resampling",
        "scale",
        "pyramid",
        "overview",
    ),
    RiskClass.HYDROLOGY: (
        "hydro",
        "flow",
        "fill",
        "burn",
        "depression",
        "sink",
        "conditioning",
    ),
    RiskClass.AGGREGATION: (
        "aggregate",
        "aggregation",
        "zonal",
        "summary",
        "statistics",
    ),
}

# Canonical justification domain names for each risk class
JUSTIFICATION_DOMAIN: dict[RiskClass, str] = {
    RiskClass.CRS_DATUM: "crs_datum_justification",
    RiskClass.RESAMPLING: "resampling_justification",
    RiskClass.HYDROLOGY: "hydrology_justification",
    RiskClass.AGGREGATION: "aggregation_justification",
}

RESOURCE_KEY: dict[RiskClass, str] = {
    RiskClass.CRS_DATUM: "crs",
    RiskClass.RESAMPLING: "resampling",
    RiskClass.HYDROLOGY: "hydrology",
    RiskClass.AGGREGATION: "aggregation",
}

# Argument names signalling specific risk classes
_ARG_KEYWORDS: dict[RiskClass, tuple[str, ...]] = {
    RiskClass.CRS_DATUM: (
        "dst_crs",
        "target_crs",
        "datum",
        "target_datum",
    ),
    RiskClass.RESAMPLING: (
        "resampling",
        "method",
        "interpolation",
        "source_resolution",
        "target_resolution",
    ),
    RiskClass.HYDROLOGY: (
        "flowdir",
        "hydrology",
        "conditioning",
        "burn_streams",
        "fill_depressions",
    ),
    RiskClass.AGGREGATION: (
        "stat",
        "statistics",
        "aggregation",
        "zones",
        "zone_layer",
    ),
}

# Argument keys to retain when hashing / generating context
_RELEVANT_ARG_KEYS: dict[RiskClass, tuple[str, ...]] = {
    RiskClass.CRS_DATUM: (
        "source_crs",
        "src_crs",
        "dst_crs",
        "target_crs",
        "datum",
        "target_datum",
        "bounds",
        "resolution",
        "width",
        "height",
    ),
    RiskClass.RESAMPLING: (
        "resampling",
        "method",
        "source_resolution",
        "target_resolution",
        "scale_factor",
        "data_type",
    ),
    RiskClass.HYDROLOGY: (
        "conditioning_method",
        "flowdir",
        "fill_depressions",
        "breach_depressions",
        "burn_streams",
        "snap_pour_points",
        "dem_crs",
    ),
    RiskClass.AGGREGATION: (
        "aggregation_type",
        "stat",
        "statistics",
        "zones",
        "zone_layer",
        "weight_field",
    ),
}


def classify(tool_name: str, args: Mapping[str, Any]) -> RiskClass:
    """Classify a tool invocation into an epistemic risk class."""
    tool_lower = tool_name.lower()
    # Tool name heuristics
    for risk, keywords in _TOOL_KEYWORDS.items():
        if any(keyword in tool_lower for keyword in keywords):
            return risk

    normalized_args = _flatten_args(args)
    # Argument-based heuristics
    for risk, keywords in _ARG_KEYWORDS.items():
        if any(key in normalized_args for key in keywords):
            return risk

    return RiskClass.NONE


def extract_relevant_args(risk: RiskClass, args: Mapping[str, Any]) -> dict[str, Any]:
    """Return a filtered, JSON-serialisable dict of arguments relevant to the risk."""
    flat = _flatten_args(args)
    if risk is RiskClass.NONE:
        return {}

    allowed = _RELEVANT_ARG_KEYS.get(risk, ())
    if not allowed:
        return {}

    filtered = {key: flat[key] for key in allowed if key in flat}
    return _to_primitive(filtered)


def input_hash(risk: RiskClass, tool_name: str, args: Mapping[str, Any]) -> str:
    """Generate a stable hash for epistemic cache lookup."""
    payload = {
        "risk": risk.name,
        "tool": tool_name,
        "args": extract_relevant_args(risk, args),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def _flatten_args(args: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten common call argument containers (e.g., params models)."""
    flat: dict[str, Any] = {}
    for key, value in args.items():
        key_lower = str(key)
        if key_lower in {"params", "arguments", "options"} and isinstance(value, Mapping):
            for nested_key, nested_value in value.items():
                flat[str(nested_key)] = nested_value
        elif hasattr(value, "model_dump") and callable(value.model_dump):
            dumped = value.model_dump()
            if isinstance(dumped, Mapping):
                for nested_key, nested_value in dumped.items():
                    flat[str(nested_key)] = nested_value
        else:
            flat[key_lower] = value

    return flat


def _to_primitive(value: Any) -> Any:
    """Recursively convert input to JSON-serialisable primitives."""
    if isinstance(value, Mapping):
        return {str(k): _to_primitive(v) for k, v in value.items()}
    if isinstance(value, list | tuple | set):
        return [_to_primitive(v) for v in value]
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _to_primitive(value.model_dump())
    if hasattr(value, "dict") and callable(value.dict):  # Pydantic v1 compatibility
        return _to_primitive(value.dict())
    return value
