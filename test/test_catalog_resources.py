"""Tests for workspace catalog resources."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from src.config import reset_workspaces_cache
from src.resources.catalog.base import collect_entries
from src.shared.catalog import clear_cache, scan

EXPECTED_SERIALIZED_TOTAL = 2


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Provision a temporary workspace and ensure caches reset around each test."""
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    monkeypatch.setenv("GDAL_MCP_WORKSPACES", str(workspace_root))
    reset_workspaces_cache()
    clear_cache()
    yield workspace_root
    clear_cache()
    reset_workspaces_cache()


def _touch(path: Path) -> None:
    """Create an empty file, ensuring parent directories exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_scan_classifies_by_kind(workspace: Path) -> None:
    """Verify `scan()` categorises raster, vector, and other assets."""
    raster_path = workspace / "data" / "dem.tif"
    vector_path = workspace / "data" / "roads.geojson"
    other_path = workspace / "notes" / "readme.txt"

    _touch(raster_path)
    _touch(vector_path)
    _touch(other_path)

    entries = scan(kind="all")
    kinds = {entry.ref.path: entry.kind for entry in entries}

    assert kinds[str(raster_path.resolve())] == "raster"
    assert kinds[str(vector_path.resolve())] == "vector"
    assert kinds[str(other_path.resolve())] == "other"

    raster_entries = scan(kind="raster")
    assert {entry.ref.path for entry in raster_entries} == {str(raster_path.resolve())}

    vector_entries = scan(kind="vector")
    assert {entry.ref.path for entry in vector_entries} == {str(vector_path.resolve())}


def test_scan_respects_hidden_flag(workspace: Path) -> None:
    """Ensure hidden files remain excluded unless explicitly requested."""
    visible = workspace / "data" / "visible.tif"
    hidden = workspace / "data" / ".hidden.tif"

    _touch(visible)
    _touch(hidden)

    default_entries = scan(kind="raster")
    assert {entry.ref.path for entry in default_entries} == {str(visible.resolve())}

    hidden_entries = scan(kind="raster", include_hidden=True)
    assert {entry.ref.path for entry in hidden_entries} == {
        str(visible.resolve()),
        str(hidden.resolve()),
    }


def test_catalog_collect_entries_return_serializable_payloads(workspace: Path) -> None:
    """Catalog resources should emit serialisable payloads with expected counts."""
    raster_path = workspace / "rasters" / "elevation.vrt"
    vector_path = workspace / "vectors" / "buildings.geojson"

    _touch(raster_path)
    _touch(vector_path)

    all_payload = collect_entries(ctx=None, kind="all").model_dump()
    assert all_payload["total"] == EXPECTED_SERIALIZED_TOTAL
    assert all_payload["kind"] is None

    raster_payload = collect_entries(ctx=None, kind="raster").model_dump()
    assert raster_payload["kind"] == "raster"
    assert {entry["path"] for entry in raster_payload["entries"]} == {str(raster_path.resolve())}

    vector_payload = collect_entries(ctx=None, kind="vector").model_dump()
    assert vector_payload["kind"] == "vector"
    assert {entry["path"] for entry in vector_payload["entries"]} == {str(vector_path.resolve())}
