"""Catalog resources exposing workspace discovery."""

from .all import list_all
from .raster import list_raster
from .vector import list_vector

__all__ = [
    "list_all",
    "list_raster",
    "list_vector",
]
