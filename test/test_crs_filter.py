"""Tests for CRS-based catalog filtering."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from src.config import reset_workspaces_cache
from src.shared.catalog import clear_cache, filter_by_crs


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


def _create_raster(path: Path, crs_code: str, width: int = 10, height: int = 10) -> None:
    """Create a minimal test raster with specified CRS."""
    path.parent.mkdir(parents=True, exist_ok=True)

    transform = from_bounds(0, 0, width, height, width, height)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=rasterio.uint8,
        crs=CRS.from_string(crs_code),
        transform=transform,
    ) as dst:
        # Write a simple array
        data = np.ones((height, width), dtype=np.uint8)
        dst.write(data, 1)


def test_filter_by_crs_empty_workspace(workspace: Path) -> None:
    """Verify CRS filter works on empty workspace."""
    entries = filter_by_crs(crs_code="EPSG:4326")
    assert len(entries) == 0


def test_filter_by_crs_single_match(workspace: Path) -> None:
    """Verify CRS filter finds datasets with matching CRS."""
    # Create raster in WGS84
    wgs84_file = workspace / "data" / "wgs84.tif"
    _create_raster(wgs84_file, "EPSG:4326")

    # Create raster in Web Mercator
    webmerc_file = workspace / "data" / "webmerc.tif"
    _create_raster(webmerc_file, "EPSG:3857")

    # Filter for WGS84
    wgs84_entries = filter_by_crs(crs_code="EPSG:4326")
    assert len(wgs84_entries) == 1
    assert wgs84_entries[0].ref.path == str(wgs84_file.resolve())

    # Filter for Web Mercator
    webmerc_entries = filter_by_crs(crs_code="EPSG:3857")
    assert len(webmerc_entries) == 1
    assert webmerc_entries[0].ref.path == str(webmerc_file.resolve())


def test_filter_by_crs_multiple_matches(workspace: Path) -> None:
    """Verify CRS filter finds all matching datasets."""
    # Create multiple WGS84 rasters
    files = [
        workspace / "data" / "wgs84_1.tif",
        workspace / "data" / "wgs84_2.tif",
        workspace / "data" / "wgs84_3.tif",
    ]

    for f in files:
        _create_raster(f, "EPSG:4326")

    # Create one Web Mercator raster
    _create_raster(workspace / "data" / "webmerc.tif", "EPSG:3857")

    # Filter for WGS84
    entries = filter_by_crs(crs_code="EPSG:4326")
    assert len(entries) == 3

    # Verify all paths are in the results
    paths = {e.ref.path for e in entries}
    expected = {str(f.resolve()) for f in files}
    assert paths == expected


def test_filter_by_crs_normalization(workspace: Path) -> None:
    """Verify CRS code normalization works."""
    # Create WGS84 raster
    wgs84_file = workspace / "data" / "wgs84.tif"
    _create_raster(wgs84_file, "EPSG:4326")

    # Test various input formats
    test_codes = [
        "EPSG:4326",  # Standard format
        "epsg:4326",  # Lowercase
        "4326",  # Just the number
    ]

    for code in test_codes:
        entries = filter_by_crs(crs_code=code)
        assert len(entries) == 1, f"Failed for CRS code: {code}"
        assert entries[0].ref.path == str(wgs84_file.resolve())


def test_filter_by_crs_kind_filter(workspace: Path) -> None:
    """Verify CRS filter respects kind parameter."""
    # Create WGS84 raster
    _create_raster(workspace / "data" / "wgs84.tif", "EPSG:4326")

    # Filter for rasters
    raster_entries = filter_by_crs(crs_code="EPSG:4326", kind="raster")
    assert len(raster_entries) == 1

    # Filter for vectors (should be empty)
    vector_entries = filter_by_crs(crs_code="EPSG:4326", kind="vector")
    assert len(vector_entries) == 0


def test_filter_by_crs_no_matches(workspace: Path) -> None:
    """Verify CRS filter returns empty list when no datasets match."""
    # Create WGS84 raster
    _create_raster(workspace / "data" / "wgs84.tif", "EPSG:4326")

    # Filter for different CRS
    entries = filter_by_crs(crs_code="EPSG:32610")  # UTM Zone 10N
    assert len(entries) == 0


def test_filter_by_crs_skips_non_geospatial(workspace: Path) -> None:
    """Verify CRS filter ignores non-geospatial files."""
    # Create WGS84 raster
    _create_raster(workspace / "data" / "wgs84.tif", "EPSG:4326")

    # Create non-geospatial file
    txt_file = workspace / "notes" / "readme.txt"
    txt_file.parent.mkdir(parents=True, exist_ok=True)
    txt_file.write_text("hello")

    # Filter should only find the raster
    entries = filter_by_crs(crs_code="EPSG:4326")
    assert len(entries) == 1
    assert entries[0].kind == "raster"
