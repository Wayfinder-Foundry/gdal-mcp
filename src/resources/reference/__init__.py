"""Reference resources exposing domain knowledge and system capabilities."""

from .compression import list_compression_methods_resource
from .crs import list_common_crs
from .glossary import list_geospatial_terms
from .resampling import list_resampling_methods_resource, resampling_guide_resource

__all__ = [
    "list_common_crs",
    "list_resampling_methods_resource",
    "resampling_guide_resource",
    "list_compression_methods_resource",
    "list_geospatial_terms",
]
