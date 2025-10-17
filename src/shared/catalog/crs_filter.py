"""CRS-based catalog filtering for workspace datasets."""

from __future__ import annotations

from pathlib import Path

from fastmcp import Context

from src.shared.catalog.scanner import CatalogEntry, CatalogKind, scan
from src.shared.metadata.format_detection import read_format_metadata


def filter_by_crs(
    *,
    crs_code: str,
    kind: CatalogKind = "all",
    include_hidden: bool = False,
    ctx: Context | None = None,
) -> list[CatalogEntry]:
    """Filter workspace catalog entries by CRS.

    Args:
        crs_code: CRS identifier to filter by (e.g., "EPSG:4326", "EPSG:3857")
        kind: Dataset kind filter ("all", "raster", "vector")
        include_hidden: Whether to include hidden files
        ctx: Optional context for logging

    Returns:
        List of catalog entries matching the specified CRS
    """
    # Normalize CRS code for comparison
    normalized_target = _normalize_crs(crs_code)

    if ctx:
        ctx.info(f"[crs_filter] Filtering catalog for CRS: {normalized_target}")  # type: ignore[unused-coroutine]

    # Get all entries
    all_entries = scan(kind=kind, include_hidden=include_hidden, ctx=ctx)

    # Filter by CRS
    matched_entries = []
    for entry in all_entries:
        if entry.kind == "other":
            # Skip non-geospatial files
            continue

        path_str = entry.ref.path
        if not path_str:
            continue

        path = Path(path_str)
        if not path.exists():
            continue

        # Get CRS from metadata
        try:
            meta = read_format_metadata(path_str)
            details = meta.get("details", {})

            # Check if CRS matches
            if "crs" in details:
                file_crs = details["crs"]
                if file_crs and _normalize_crs(file_crs) == normalized_target:
                    matched_entries.append(entry)

        except Exception:
            # Skip files that can't be read
            continue

    if ctx:
        ctx.info(  # type: ignore[unused-coroutine]
            f"[crs_filter] Found {len(matched_entries)} datasets in {normalized_target}"
        )

    return matched_entries


def _normalize_crs(crs_str: str) -> str:
    """Normalize CRS string for comparison.

    Handles variations like:
    - "EPSG:4326" vs "epsg:4326"
    - "EPSG:4326" vs "4326"
    - Full WKT vs EPSG code

    Args:
        crs_str: CRS string to normalize

    Returns:
        Normalized CRS string in uppercase EPSG:XXXX format
    """
    if not crs_str:
        return ""

    crs_upper = crs_str.upper().strip()

    # If it's already in EPSG:XXXX format, return as-is
    if crs_upper.startswith("EPSG:"):
        return crs_upper

    # If it's just a number, add EPSG: prefix
    if crs_upper.isdigit():
        return f"EPSG:{crs_upper}"

    # Try to extract EPSG code from WKT or other formats
    if "EPSG" in crs_upper:
        # Find EPSG code in string like 'AUTHORITY["EPSG","4326"]'
        import re

        match = re.search(r'EPSG["\s,:]+(\d+)', crs_upper)
        if match:
            return f"EPSG:{match.group(1)}"

    # Return as-is if we can't normalize
    return crs_upper
