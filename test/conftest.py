"""Pytest configuration and fixtures for gdal-mcp tests."""
from __future__ import annotations

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from pathlib import Path


@pytest.fixture
def test_data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test data."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def tiny_raster_gtiff(test_data_dir: Path) -> Path:
    """Create a tiny 10x10 single-band GeoTIFF for testing."""
    output_path = test_data_dir / "tiny_raster.tif"
    
    # Create a simple gradient array
    data = np.arange(100, dtype=np.uint8).reshape(10, 10)
    
    # Define geotransform: 1-degree pixels starting at (0, 0)
    transform = from_origin(0, 10, 1, 1)
    
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=255,
    ) as dst:
        dst.write(data, 1)
        dst.update_tags(description="Test raster")
    
    return output_path


@pytest.fixture
def tiny_raster_rgb(test_data_dir: Path) -> Path:
    """Create a tiny 10x10 3-band RGB GeoTIFF for testing."""
    output_path = test_data_dir / "tiny_rgb.tif"
    
    # Create RGB bands
    red = np.full((10, 10), 100, dtype=np.uint8)
    green = np.full((10, 10), 150, dtype=np.uint8)
    blue = np.full((10, 10), 200, dtype=np.uint8)
    
    transform = from_origin(0, 10, 1, 1)
    
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=3,
        dtype=np.uint8,
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(red, 1)
        dst.write(green, 2)
        dst.write(blue, 3)
    
    return output_path


@pytest.fixture
def tiny_raster_with_nodata(test_data_dir: Path) -> Path:
    """Create a tiny raster with nodata values for statistics testing."""
    output_path = test_data_dir / "tiny_nodata.tif"
    
    # Create data with some nodata (255) values
    data = np.arange(100, dtype=np.uint8).reshape(10, 10)
    data[0:2, 0:2] = 255  # Set top-left corner to nodata
    
    transform = from_origin(0, 10, 1, 1)
    
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype=data.dtype,
        crs="EPSG:4326",
        transform=transform,
        nodata=255,
    ) as dst:
        dst.write(data, 1)
    
    return output_path


@pytest.fixture
def tiny_vector_geojson(test_data_dir: Path) -> Path:
    """Create a tiny GeoJSON file for vector testing."""
    output_path = test_data_dir / "tiny_vector.geojson"
    
    geojson_content = """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [0.0, 0.0]
      },
      "properties": {
        "name": "Point A",
        "value": 100
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [1.0, 1.0]
      },
      "properties": {
        "name": "Point B",
        "value": 200
      }
    },
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [[2.0, 2.0], [3.0, 2.0], [3.0, 3.0], [2.0, 3.0], [2.0, 2.0]]
        ]
      },
      "properties": {
        "name": "Polygon C",
        "value": 300
      }
    }
  ]
}"""
    
    output_path.write_text(geojson_content)
    return output_path
