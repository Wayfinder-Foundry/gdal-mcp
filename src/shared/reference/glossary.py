"""Geospatial terminology glossary for AI agent context."""

from __future__ import annotations

from enum import Enum
from typing import TypedDict

try:  # Python 3.11+
    from enum import StrEnum
except ImportError:  # pragma: no cover - backport for Python 3.10

    class StrEnum(str, Enum):
        """Minimal StrEnum backport for Python < 3.11."""

        pass


class GlossaryCategory(StrEnum):
    """High-level classification of geospatial terms."""

    CORE = "core"
    DATA = "data"
    PROCESSING = "processing"
    ANALYSIS = "analysis"
    FORMAT = "format"
    MODEL = "model"
    NETWORK = "network"
    IO = "io"
    MISC = "misc"


class GlossaryEntry(TypedDict):
    """Structured definition for a geospatial glossary term."""

    term: str
    definition: str
    category: GlossaryCategory
    example: str | None

_GLOSSARY_ENTRIES: list[GlossaryEntry] = [
    # ───── Core Concepts ──────────────────────────────────────────────
    {
        "term": "CRS",
        "definition": (
            "Coordinate Reference System describing how 2D or 3D data maps to "
            "the Earth's surface."
        ),
        "category": GlossaryCategory.CORE,
        "example": "Example: EPSG:4326 (WGS 84) defines global latitude/longitude coordinates.",
    },
    {
        "term": "EPSG",
        "definition": (
            "Standardized numeric identifier for a specific CRS, maintained by the IOGP "
            "(formerly EPSG)."
        ),
        "category": GlossaryCategory.CORE,
        "example": "Example: EPSG:3857 for Web Mercator, EPSG:3347 for Canada Lambert.",
    },
    {
        "term": "Datum",
        "definition": (
            "Reference model of the Earth's shape and size used to anchor "
            "spatial coordinates."
        ),
        "category": GlossaryCategory.CORE,
        "example": "Example: NAD83 and WGS84 are both datums.",
    },
    # ───── Data Structures ────────────────────────────────────────────
    {
        "term": "Raster",
        "definition": (
            "Grid-based dataset where each pixel stores a continuous or categorical value."
        ),
        "category": GlossaryCategory.DATA,
        "example": "Example: Elevation, temperature, or satellite imagery layers.",
    },
    {
        "term": "Vector",
        "definition": (
            "Geometry-based dataset composed of points, lines, or polygons "
            "linked to attribute tables."
        ),
        "category": GlossaryCategory.DATA,
        "example": "Example: Road networks, building footprints, or administrative boundaries.",
    },
    {
        "term": "Band",
        "definition": (
            "Single variable layer in a raster dataset; "
            "multi-band rasters hold multiple variables."
        ),
        "category": GlossaryCategory.DATA,
        "example": "Example: RGB imagery contains 3 bands (Red, Green, Blue).",
    },
    {
        "term": "DEM",
        "definition": (
            "Digital Elevation Model: a raster storing elevation values "
            "relative to sea level."
        ),
        "category": GlossaryCategory.ANALYSIS,
        "example": "Example: SRTM or Copernicus DEM tiles.",
    },
    # ───── Processing & Analysis ─────────────────────────────────────
    {
        "term": "Resampling",
        "definition": (
            "Interpolation of pixel values when changing raster resolution, "
            "grid, or CRS."
        ),
        "category": GlossaryCategory.PROCESSING,
        "example": "Methods include nearest-neighbor, bilinear, and cubic interpolation.",
    },
    {
        "term": "Reprojection",
        "definition": "Transformation of spatial data from one CRS to another.",
        "category": GlossaryCategory.PROCESSING,
        "example": "Example: Converting EPSG:4326 (lat/lon) to EPSG:3857 (Web Mercator).",
    },
    {
        "term": "Mosaic",
        "definition": (
            "Combining multiple rasters into a seamless dataset "
            "aligned to a common grid."
        ),
        "category": GlossaryCategory.PROCESSING,
        "example": "Example: Stitching several DEM tiles into one composite raster.",
    },
    {
        "term": "Clip",
        "definition": "Spatial subset of raster or vector data to a bounding polygon or extent.",
        "category": GlossaryCategory.PROCESSING,
        "example": "Example: Clipping a land-cover raster to a province boundary.",
    },
    # ───── Formats & IO ──────────────────────────────────────────────
    {
        "term": "GeoTIFF",
        "definition": "Raster file format (TIFF) embedding georeferencing information in tags.",
        "category": GlossaryCategory.FORMAT,
        "example": "Supports multiple bands, compression (e.g., LZW, ZSTD), and CRS metadata.",
    },
    {
        "term": "Shapefile",
        "definition": "Legacy Esri vector format consisting of .shp, .shx, .dbf, and .prj files.",
        "category": GlossaryCategory.FORMAT,
        "example": "Limited to 2 GB and field names ≤10 characters.",
    },
    {
        "term": "GeoPackage",
        "definition": (
            "Modern SQLite-based geospatial container for rasters, vectors, "
            "and metadata."
        ),
        "category": GlossaryCategory.FORMAT,
        "example": "Single-file alternative to Shapefile supporting SQL and large data.",
    },
    # ───── Analysis & Modeling ───────────────────────────────────────
    {
        "term": "Slope",
        "definition": "Rate of elevation change per unit distance, derived from a DEM.",
        "category": GlossaryCategory.ANALYSIS,
        "example": "Measured in degrees or percent rise.",
    },
    {
        "term": "Aspect",
        "definition": "Direction of steepest slope in terrain analysis.",
        "category": GlossaryCategory.ANALYSIS,
        "example": "Example: North-facing slopes (0°) vs south-facing (180°).",
    },
    {
        "term": "NDVI",
        "definition": "Normalized Difference Vegetation Index, derived from red and NIR bands.",
        "category": GlossaryCategory.ANALYSIS,
        "example": "NDVI = (NIR - Red) / (NIR + Red).",
    },
    # ───── Miscellaneous ─────────────────────────────────────────────
    {
        "term": "NoData",
        "definition": "Value used to represent missing or masked cells in a raster.",
        "category": GlossaryCategory.MISC,
        "example": "Commonly -9999 or NaN in floating-point datasets.",
    },
]


def get_geospatial_glossary(term: str | None = None) -> list[GlossaryEntry]:
    """
    Return glossary entries, optionally filtered by a substring match.

    Parameters
    ----------
    term : str | None
        If provided, filters terms whose names contain this substring (case-insensitive).

    Returns
    -------
    List[GlossaryEntry]
        List of glossary entries with term, definition, category, and example.
    """
    if not term:
        return list(_GLOSSARY_ENTRIES)

    needle = term.lower()
    return [entry for entry in _GLOSSARY_ENTRIES if needle in entry["term"].lower()]
