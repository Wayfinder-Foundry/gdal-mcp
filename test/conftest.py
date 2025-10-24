from __future__ import annotations

import asyncio
from pathlib import Path

import fiona
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from src.app import mcp
from src.server import mcp as server_mcp


@pytest.fixture(scope="session")
def fastmcp_server():
    """Provide the FastMCP server instance for tests."""
    assert mcp is server_mcp
    return mcp


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "asyncio: mark async test to run via asyncio.run")


def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    marker = pyfuncitem.get_closest_marker("asyncio")
    if marker and asyncio.iscoroutinefunction(pyfuncitem.obj):
        argnames = pyfuncitem._fixtureinfo.argnames
        kwargs = {name: pyfuncitem.funcargs[name] for name in argnames}
        asyncio.run(pyfuncitem.obj(**kwargs))
        return True
    return None


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


def _write_single_band(path: Path, data: np.ndarray, *, nodata: int | None = None) -> None:
    height, width = data.shape
    transform = from_origin(0, float(height), 1, 1)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=width,
        height=height,
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=nodata,
    ) as dst:
        dst.write(data, 1)


@pytest.fixture
def tiny_raster_gtiff(test_data_dir: Path) -> Path:
    path = test_data_dir / "tiny.tif"
    data = np.arange(100, dtype=np.uint8).reshape(10, 10)
    _write_single_band(path, data, nodata=255)
    return path


@pytest.fixture
def tiny_raster_rgb(test_data_dir: Path) -> Path:
    path = test_data_dir / "tiny_rgb.tif"
    base = np.arange(100, dtype=np.uint8).reshape(10, 10)
    bands = np.stack([base, base[::-1], np.full_like(base, 50)], axis=0)
    transform = from_origin(0, 10, 1, 1)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=10,
        height=10,
        count=3,
        dtype=np.uint8,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(bands)
    return path


@pytest.fixture
def tiny_raster_with_nodata(test_data_dir: Path) -> Path:
    path = test_data_dir / "tiny_nodata.tif"
    data = np.arange(100, dtype=np.uint8).reshape(10, 10)
    data[:2, :2] = 255
    _write_single_band(path, data, nodata=255)
    return path


@pytest.fixture
def tiny_vector_geojson(test_data_dir: Path) -> Path:
    path = test_data_dir / "tiny.geojson"
    schema = {"geometry": "Point", "properties": {"name": "str", "value": "int"}}
    with fiona.open(
        path,
        "w",
        driver="GeoJSON",
        schema=schema,
        crs="EPSG:4326",
    ) as dst:
        features = [
            ("A", 1, (0.0, 0.0)),
            ("B", 2, (1.0, 1.0)),
            ("C", 3, (-1.0, 0.5)),
        ]
        for name, value, (x, y) in features:
            dst.write(
                {
                    "geometry": {"type": "Point", "coordinates": (x, y)},
                    "properties": {"name": name, "value": value},
                }
            )
    return path
