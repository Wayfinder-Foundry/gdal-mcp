"""Tests for band-level raster metadata resource."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import numpy as np
import pytest
import rasterio
from fastmcp.exceptions import ToolError
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from src.config import reset_workspaces_cache
from src.shared.catalog import clear_cache
from src.shared.raster.bands import band_metadata


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


def _create_raster(path: Path, *, bands: int = 3) -> None:
    """Create a simple multi-band raster for testing."""
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 4
    height = 4
    transform = from_bounds(0, 0, width, height, width, height)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=bands,
        dtype=rasterio.uint8,
        crs=CRS.from_epsg(4326),
        transform=transform,
    ) as dst:
        descriptions = ["Red", "Green", "Blue"]
        for i in range(1, bands + 1):
            data = np.full((height, width), i, dtype=np.uint8)
            dst.write(data, i)
            if i <= len(descriptions):
                dst.set_band_description(i, descriptions[i - 1])
            dst.set_band_unit(i, "reflectance")


def test_band_metadata_basic(workspace: Path) -> None:
    """Verify band metadata reports band count and descriptions."""
    raster_path = workspace / "data" / "rgb.tif"
    _create_raster(raster_path)

    result = band_metadata(str(raster_path))

    assert result["band_count"] == 3
    bands = result["bands"]
    assert len(bands) == 3
    assert bands[0]["band"] == 1
    assert bands[0]["description"] == "Red"
    assert bands[0]["color_interpretation"] == "red"


def test_band_metadata_include_statistics(workspace: Path) -> None:
    """Verify optional statistics are returned when requested."""
    raster_path = workspace / "data" / "single.tif"
    _create_raster(raster_path, bands=1)

    result = band_metadata(str(raster_path), include_statistics=True)

    bands = result["bands"]
    stats = bands[0]["statistics"]
    assert stats is not None
    assert stats["min"] == 1
    assert stats["max"] == 1
    assert stats["mean"] == 1


def test_band_metadata_handles_missing_file(tmp_path: Path) -> None:
    """Verify ToolError is raised for missing files."""
    with pytest.raises(ToolError):
        band_metadata(str(tmp_path / "missing.tif"))
