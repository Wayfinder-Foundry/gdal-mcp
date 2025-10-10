"""Workspace dataset scanner for catalog resources."""

from __future__ import annotations

import os
import threading
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context

from src.config import get_workspaces
from src.models.resourceref import ResourceRef

CatalogKind = Literal["all", "raster", "vector"]

# Common GDAL-oriented extensions for quick classification
RASTER_EXTENSIONS = {
    ".tif",
    ".tiff",
    ".cog",
    ".vrt",
    ".img",
    ".jp2",
    ".j2k",
    ".asc",
    ".bil",
    ".bip",
    ".bsq",
    ".ers",
    ".hdf",
    ".h5",
    ".nc",
    ".grd",
    ".dem",
    ".sdat",
}

VECTOR_EXTENSIONS = {
    ".gpkg",
    ".geojson",
    ".json",
    ".shp",
    ".sqlite",
    ".kml",
    ".kmz",
    ".gml",
    ".tab",
    ".mif",
}

_EXTENSIONS_INITIALIZED = False


@dataclass(slots=True)
class CatalogEntry:
    """Catalog entry returned by the workspace scanner."""

    ref: ResourceRef
    kind: Literal["raster", "vector", "other"]
    workspace: Path
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary representation."""
        payload = self.ref.model_dump()
        payload.update(
            {
                "kind": self.kind,
                "workspace": str(self.workspace),
            }
        )
        if self.meta:
            payload.setdefault("meta", {}).update(self.meta)
        return payload


@dataclass(slots=True)
class _CacheEntry:
    signature: tuple[tuple[str, float], ...]
    data: list[CatalogEntry]


_CACHE_LOCK = threading.Lock()
_CACHE: dict[tuple, _CacheEntry] = {}


def scan(
    *,
    kind: CatalogKind = "all",
    limit: int | None = None,
    include_hidden: bool = False,
    allowed_extensions: Sequence[str] | None = None,
    ctx: Context | None = None,
) -> list[CatalogEntry]:
    """Enumerate workspace files and classify by type.

    Args:
        kind: Filter result set by category (all/raster/vector).
        limit: Maximum number of entries to return (None for unlimited).
        include_hidden: Include files or directories starting with '.'
            when True; otherwise they are skipped.
        allowed_extensions: Additional explicit extensions to include.
        ctx: Optional FastMCP context for boundary logging.

    Returns:
        List of ``CatalogEntry`` instances.
    """
    workspaces = get_workspaces()
    if not workspaces:
        # Development fallback: use current working directory
        workspaces = [Path.cwd()]

    _ensure_dynamic_extensions()

    signature = _compute_signature(workspaces, include_hidden, allowed_extensions)
    normalized_exts = tuple(sorted(normalize_extensions(allowed_extensions)))
    cache_key = (kind, include_hidden, normalized_exts)

    with _CACHE_LOCK:
        cached = _CACHE.get(cache_key)
        if cached and cached.signature == signature:
            data = cached.data
            if limit is not None and limit >= 0:
                return data[:limit]
            return list(data)

    if ctx:
        ctx_message = f"[catalog] Scanning {len(workspaces)} workspace(s)"
        _maybe_log(ctx, ctx_message)

    scanned_entries = _scan_workspaces(
        workspaces,
        include_hidden=include_hidden,
        allowed_extensions=allowed_extensions,
    )

    if kind != "all":
        scanned_entries = [entry for entry in scanned_entries if entry.kind == kind]

    with _CACHE_LOCK:
        _CACHE[cache_key] = _CacheEntry(signature=signature, data=list(scanned_entries))

    if limit is not None and limit >= 0:
        return scanned_entries[:limit]
    return scanned_entries


def _scan_workspaces(
    workspaces: Sequence[Path],
    *,
    include_hidden: bool,
    allowed_extensions: Sequence[str] | None,
) -> list[CatalogEntry]:
    normalized_allowed = (
        set(normalize_extensions(allowed_extensions)) if allowed_extensions else None
    )
    entries: list[CatalogEntry] = []

    for workspace in workspaces:
        if not workspace.exists():
            continue

        for path in _iter_files(workspace, include_hidden):
            if normalized_allowed is not None and path.suffix.lower() not in normalized_allowed:
                continue

            kind = _classify(path)
            ref = ResourceRef(
                uri=path.resolve().as_uri(),
                path=str(path.resolve()),
                size=_safe_stat_size(path),
                driver=None,
                meta={},
            )
            entry = CatalogEntry(ref=ref, kind=kind, workspace=workspace)
            entries.append(entry)

    entries.sort(key=lambda e: e.ref.path or e.ref.uri)
    return entries


def _iter_files(root: Path, include_hidden: bool) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        current_path = Path(dirpath)
        if not include_hidden:
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for filename in filenames:
            if not include_hidden and filename.startswith("."):
                continue
            path = current_path / filename
            if path.is_file():
                yield path


def _classify(path: Path) -> Literal["raster", "vector", "other"]:
    suffix = path.suffix.lower()
    if suffix in RASTER_EXTENSIONS:
        return "raster"
    if suffix in VECTOR_EXTENSIONS:
        return "vector"
    if suffix == ".zip":
        # Heuristic: zipped shapefile/geopackage
        lower_name = path.name.lower()
        if any(token in lower_name for token in ("shapefile", "vector", "gpkg")):
            return "vector"
    return "other"


def normalize_extensions(exts: Iterable[str] | None) -> list[str]:
    """Normalize file extensions to lowercase without leading dot."""
    if not exts:
        return []
    normalized: list[str] = []
    for ext in exts:
        if not ext:
            continue
        ext = ext.lower()
        if not ext.startswith("."):
            ext = "." + ext
        normalized.append(ext)
    return normalized


def _safe_stat_size(path: Path) -> int | None:
    try:
        return path.stat().st_size
    except OSError:
        return None


def _compute_signature(
    workspaces: Sequence[Path],
    include_hidden: bool,
    allowed_extensions: Sequence[str] | None,
) -> tuple[tuple[str, float], ...]:
    normalized_extensions = tuple(sorted(normalize_extensions(allowed_extensions)))
    signature: list[tuple[str, float]] = []
    for workspace in workspaces:
        try:
            mtime = workspace.stat().st_mtime
        except OSError:
            mtime = 0.0
        signature.append((str(workspace.resolve()), mtime))
    signature.sort()
    signature.append(("__hidden__", 1.0 if include_hidden else 0.0))
    signature.append(("__ext__", hash(normalized_extensions)))
    return tuple(signature)


def _maybe_log(ctx: Context, message: str) -> None:
    try:
        import asyncio

        if asyncio.get_event_loop().is_running():
            asyncio.create_task(ctx.info(message))
        else:
            asyncio.run(ctx.info(message))
    except Exception:
        # Best effort logging only
        pass


def _ensure_dynamic_extensions() -> None:
    global _EXTENSIONS_INITIALIZED
    if _EXTENSIONS_INITIALIZED:
        return

    _extend_raster_extensions()
    _extend_vector_extensions()

    _EXTENSIONS_INITIALIZED = True


def clear_cache() -> None:
    """Reset catalog scan cache and dynamic extension state (testing helper)."""
    global _EXTENSIONS_INITIALIZED
    with _CACHE_LOCK:
        _CACHE.clear()
    _EXTENSIONS_INITIALIZED = False


def _extend_raster_extensions() -> None:
    try:
        import rasterio

        try:
            driver_map = rasterio.drivers.raster_driver_extensions()
        except AttributeError:
            driver_map = {}

        for extensions in driver_map.values():
            for ext in extensions or []:
                if not ext:
                    continue
                ext = ext.lower()
                if not ext.startswith("."):
                    ext = "." + ext
                RASTER_EXTENSIONS.add(ext)
    except ImportError:
        pass


def _extend_vector_extensions() -> None:
    try:
        import pyogrio

        try:
            driver_info = pyogrio.list_drivers()
        except Exception:
            driver_info = {}

        for info in driver_info.values():
            extensions = info.get("extensions", []) if isinstance(info, dict) else []
            for ext in extensions or []:
                if not ext:
                    continue
                ext = ext.lower()
                if not ext.startswith("."):
                    ext = "." + ext
                VECTOR_EXTENSIONS.add(ext)
    except ImportError:
        pass
