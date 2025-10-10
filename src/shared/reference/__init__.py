"""Shared data and helpers for reference resources."""

from .compression import Compression, CompressionInfo, list_compression_methods
from .crs import get_common_crs
from .glossary import GlossaryCategory, GlossaryEntry, get_geospatial_glossary
from .resampling import (
    Category,
    OpType,
    ResamplingInfo,
    choose_resampling,
    list_resampling_methods,
    normalize_resampling,
    resampling_guide,
)

__all__ = [
    "get_common_crs",
    "Category",
    "OpType",
    "ResamplingInfo",
    "list_resampling_methods",
    "resampling_guide",
    "normalize_resampling",
    "choose_resampling",
    "Compression",
    "CompressionInfo",
    "list_compression_methods",
    "GlossaryCategory",
    "GlossaryEntry",
    "get_geospatial_glossary",
]
