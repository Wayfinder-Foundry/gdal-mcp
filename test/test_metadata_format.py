from __future__ import annotations

from pathlib import Path

import pytest

from src.shared.metadata.format_detection import read_format_metadata


def test_read_format_metadata_raster(tiny_raster_gtiff: Path) -> None:
    info = read_format_metadata(str(tiny_raster_gtiff))
    assert info["category"] == "raster"
    assert info["driver"] in {"GTiff", "GTiff/GeoTIFF"}
    assert info["details"]["band_count"] == 1
    assert info["details"]["width"] == 10
    assert info["details"]["height"] == 10


def test_read_format_metadata_vector(tiny_vector_geojson: Path) -> None:
    pytest.importorskip("pyogrio", reason="pyogrio required for vector format test")
    info = read_format_metadata(str(tiny_vector_geojson))
    assert info["category"] == "vector"
    assert info["driver"] is not None
    assert "details" in info


def test_read_format_metadata_unknown(tmp_path: Path) -> None:
    txt_path = tmp_path / "notes.txt"
    txt_path.write_text("hello")
    info = read_format_metadata(str(txt_path))
    assert info["category"] == "unknown"
    assert info["driver"] is None


def test_read_format_metadata_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        read_format_metadata("/tmp/does-not-exist.tif")
