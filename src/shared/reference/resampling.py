"""Resampling method registry and selection heuristics for raster operations."""

from __future__ import annotations

from enum import Enum

try:  # Python 3.11+
    from enum import StrEnum
except ImportError:  # pragma: no cover - backport for Python 3.10

    class StrEnum(str, Enum):
        """Minimal StrEnum backport for Python < 3.11."""

        pass


from collections.abc import Mapping, Sequence
from functools import lru_cache
from types import MappingProxyType
from typing import Final, TypedDict

try:
    from rasterio.enums import Resampling as _RIOResampling
except ImportError:  # pragma: no cover - optional
    _RIOResampling = None  # type: ignore


AliasTuple = tuple[str, ...]
EMPTY_ALIASES: Final[AliasTuple] = ()


# ────────────────── Schema ──────────────────


class OpType(StrEnum):
    """Resampling operation type: interpolate or aggregate."""

    INTERPOLATE = "interpolate"
    AGGREGATE = "aggregate"


class Category(StrEnum):
    """Data category: continuous, categorical, or generic."""

    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"
    GENERIC = "generic"


class ResamplingInfo(TypedDict):
    """Metadata for a single resampling method."""

    name: str  # UPPER_SNAKE
    value: int | str  # rasterio enum .value if available; else gdal token
    description: str
    recommended_usage: str
    category: Category
    op_type: OpType
    gdal_name: str  # gdalwarp -r token
    aliases: list[str]  # normalized lowercase aliases


# ─────────────── Constants (frozen) ───────────────

_DESC: Final[Mapping[str, str]] = MappingProxyType(
    {
        "nearest": "Nearest neighbour (fast, preserves original values).",
        "bilinear": "Bilinear interpolation (smooths continuous surfaces).",
        "cubic": "Cubic convolution (balances sharpness and smoothness).",
        "cubic_spline": "Cubic spline interpolation (very smooth; may overshoot).",
        "lanczos": "Lanczos filter (high-quality resampling for imagery).",
        "average": "Average of contributing pixels (aggregation/decimation).",
        "mode": "Mode (majority) of contributing pixels (categorical).",
        "gauss": "Gaussian prefiltering before decimation.",
        "min": "Minimum value over the pixel footprint.",
        "max": "Maximum value over the pixel footprint.",
        "med": "Median value over the pixel footprint.",
        "q1": "First quartile of contributing pixel values.",
        "q3": "Third quartile of contributing pixel values.",
        "sum": "Sum of contributing pixels (e.g., counts).",
        "rms": "Root-mean-square over contributing pixels.",
    }
)

_USE: Final[Mapping[str, str]] = MappingProxyType(
    {
        "nearest": "Categorical rasters (classes, masks); any scale.",
        "bilinear": "Continuous rasters (elevation, temperature); up/downsample.",
        "cubic": "Continuous rasters with emphasis on quality; up/downsample.",
        "cubic_spline": "High-quality visualization of continuous rasters.",
        "lanczos": "Orthophotos / high-res imagery where detail matters (upsampling).",
        "average": "Downsampling continuous rasters (noise reduction).",
        "mode": "Downsampling categorical rasters (generalization).",
        "gauss": "Downsampling imagery with prefilter to reduce aliasing.",
        "min": "Hydrology, hazards—preserve minima on decimation.",
        "max": "Hazards/peaks—preserve maxima on decimation.",
        "med": "Robust downsampling of noisy continuous rasters.",
        "q1": "Distribution-aware aggregation (lower tail).",
        "q3": "Distribution-aware aggregation (upper tail).",
        "sum": "Counts/accumulations—area-weighted totals when rescaling.",
        "rms": "Energy-like measures; error metrics.",
    }
)

_GDAL_NAME: Final[Mapping[str, str]] = MappingProxyType(
    {
        "nearest": "nearest",
        "bilinear": "bilinear",
        "cubic": "cubic",
        "cubic_spline": "cubicspline",
        "lanczos": "lanczos",
        "average": "average",
        "mode": "mode",
        "gauss": "gauss",
        "min": "min",
        "max": "max",
        "med": "med",
        "q1": "q1",
        "q3": "q3",
        "sum": "sum",
        "rms": "rms",
    }
)


_ALIASES: Final[Mapping[str, AliasTuple]] = MappingProxyType(
    {
        "cubic_spline": ("cubicspline", "cubic-spline", "cubic spline"),
        "nearest": ("nearest_neighbour", "nearest_neighbor", "nn"),
        "bilinear": ("bi-linear",),
        "rms": ("root_mean_square", "root-mean-square"),
    }
)

_OP: Final[Mapping[str, OpType]] = MappingProxyType(
    {
        "nearest": OpType.INTERPOLATE,
        "bilinear": OpType.INTERPOLATE,
        "cubic": OpType.INTERPOLATE,
        "cubic_spline": OpType.INTERPOLATE,
        "lanczos": OpType.INTERPOLATE,
        "average": OpType.AGGREGATE,
        "mode": OpType.AGGREGATE,
        "gauss": OpType.AGGREGATE,
        "min": OpType.AGGREGATE,
        "max": OpType.AGGREGATE,
        "med": OpType.AGGREGATE,
        "q1": OpType.AGGREGATE,
        "q3": OpType.AGGREGATE,
        "sum": OpType.AGGREGATE,
        "rms": OpType.AGGREGATE,
    }
)

_CAT: Final[Mapping[str, Category]] = MappingProxyType(
    {
        "nearest": Category.CATEGORICAL,
        "mode": Category.CATEGORICAL,
        "bilinear": Category.CONTINUOUS,
        "cubic": Category.CONTINUOUS,
        "cubic_spline": Category.CONTINUOUS,
        "lanczos": Category.CONTINUOUS,
        "average": Category.CONTINUOUS,
        "gauss": Category.CONTINUOUS,
        "min": Category.CONTINUOUS,
        "max": Category.CONTINUOUS,
        "med": Category.CONTINUOUS,
        "q1": Category.CONTINUOUS,
        "q3": Category.CONTINUOUS,
        "sum": Category.CONTINUOUS,
        "rms": Category.CONTINUOUS,
    }
)

# Static, precomputed guide (frozen)
_GUIDE: Final[Sequence[dict[str, str]]] = (
    {
        "method": "nearest",
        "best_for": "Categorical data (classes, masks)",
        "notes": "Preserves labels; no smoothing.",
        "op_type": OpType.INTERPOLATE,
    },
    {
        "method": "bilinear",
        "best_for": "Continuous surfaces (temperature, elevation)",
        "notes": "Smooths output; can blur edges.",
        "op_type": OpType.INTERPOLATE,
    },
    {
        "method": "cubic",
        "best_for": "Imagery/DEMs needing quality",
        "notes": "Sharper than bilinear; minor overshoot possible.",
        "op_type": OpType.INTERPOLATE,
    },
    {
        "method": "lanczos",
        "best_for": "High-resolution imagery (upsampling)",
        "notes": "High quality; heavier compute.",
        "op_type": OpType.INTERPOLATE,
    },
    {
        "method": "average",
        "best_for": "Downsampling continuous rasters",
        "notes": "Reduces noise via aggregation.",
        "op_type": OpType.AGGREGATE,
    },
    {
        "method": "mode",
        "best_for": "Downsampling categorical rasters",
        "notes": "Majority class in window.",
        "op_type": OpType.AGGREGATE,
    },
    {
        "method": "gauss",
        "best_for": "Downsampling imagery with anti-aliasing",
        "notes": "Prefilter helps avoid aliasing.",
        "op_type": OpType.AGGREGATE,
    },
)

# ─────────────── Registry build (once) ───────────────


def _rio_value_or_gdal_token(key: str) -> int | str:
    if _RIOResampling is not None:
        name_upper = key.upper()
        if hasattr(_RIOResampling, name_upper):
            return getattr(_RIOResampling, name_upper).value
    return _GDAL_NAME[key]


def _build_registry() -> list[ResamplingInfo]:
    entries: list[ResamplingInfo] = []
    for key in _DESC.keys():
        name: str = key.upper()
        value: int | str = _rio_value_or_gdal_token(key)
        description: str = _DESC[key]
        recommended_usage: str = _USE.get(key, "")
        category: Category = _CAT.get(key, Category.GENERIC)
        op_type: OpType = _OP[key]
        gdal_name: str = _GDAL_NAME[key]
        alias_tuple: AliasTuple = _ALIASES.get(key, EMPTY_ALIASES)
        aliases_list: list[str] = [key, *alias_tuple]

        entry: ResamplingInfo = {
            "name": name,
            "value": value,
            "description": description,
            "recommended_usage": recommended_usage,
            "category": category,
            "op_type": op_type,
            "gdal_name": gdal_name,
            "aliases": aliases_list,
        }
        entries.append(entry)

    entries.sort(key=lambda e: e["name"])
    return entries


_REGISTRY: Final[list[ResamplingInfo]] = _build_registry()

# Fast lookups (precomputed)
_BY_CANON: Final[Mapping[str, ResamplingInfo]] = MappingProxyType(
    {e["name"].lower(): e for e in _REGISTRY}
)
_BY_GDAL: Final[Mapping[str, ResamplingInfo]] = MappingProxyType(
    {e["gdal_name"]: e for e in _REGISTRY}
)
_BY_ALIAS: Final[Mapping[str, ResamplingInfo]] = MappingProxyType(
    {alias: e for e in _REGISTRY for alias in e["aliases"]}
)


# ────────────────── Public API ──────────────────


def list_resampling_methods(
    *, category: str | None = None, op_type: str | None = None
) -> list[ResamplingInfo]:
    """List resampling methods, optionally filtered by category or operation type."""
    methods: Sequence[ResamplingInfo] = _REGISTRY
    if category:
        c = category.lower()
        methods = [m for m in methods if m["category"].value == c]
    if op_type:
        o = op_type.lower()
        methods = [m for m in methods if m["op_type"].value == o]
    # return a shallow copy to avoid accidental external mutation
    return list(methods)


def resampling_guide(topic: str | None = None) -> list[dict[str, str]]:
    """Return resampling guidance entries, optionally filtered by topic."""
    if not topic:
        return list(_GUIDE)  # shallow copy of static sequence
    t = topic.lower()
    return [g for g in _GUIDE if t in g["method"] or t in g["best_for"].lower()]


@lru_cache(maxsize=128)
def normalize_resampling(name_or_alias: str) -> ResamplingInfo | None:
    """Normalize a resampling method name or alias to canonical ResamplingInfo."""
    needle = name_or_alias.strip().lower()
    return _BY_GDAL.get(needle) or _BY_ALIAS.get(needle) or _BY_CANON.get(needle)


def choose_resampling(*, is_categorical: bool, scale_ratio: float) -> ResamplingInfo:
    """Choose an appropriate resampling method based on data type and scale ratio."""
    if is_categorical:
        return (
            normalize_resampling("mode") if scale_ratio < 1.0 else normalize_resampling("nearest")
        )  # type: ignore
    if scale_ratio > 1.0:
        return normalize_resampling("lanczos") or normalize_resampling("cubic")  # type: ignore
    if scale_ratio < 1.0:
        return normalize_resampling("gauss") or normalize_resampling("average")  # type: ignore
    return normalize_resampling("nearest")  # type: ignore


__all__ = [
    "ResamplingInfo",
    "OpType",
    "Category",
    "list_resampling_methods",
    "resampling_guide",
    "normalize_resampling",
    "choose_resampling",
]
