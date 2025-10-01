"""Unit tests for vector tools."""

from __future__ import annotations

import pytest
from pathlib import Path

# Import the core logic function (not the @mcp.tool wrapped version)
from src.tools.vector.info import _info


@pytest.mark.asyncio
async def test_vector_info_geojson(tiny_vector_geojson: Path):
    """Test vector.info on a GeoJSON file."""
    result = await _info(str(tiny_vector_geojson))

    assert result.path == str(tiny_vector_geojson)
    assert result.driver in ["GeoJSON", "ESRI Shapefile"]  # Driver may vary
    assert result.feature_count == 3
    assert len(result.fields) >= 2  # name, value fields

    # Check for geometry types
    assert len(result.geometry_types) > 0


@pytest.mark.asyncio
async def test_vector_info_fields(tiny_vector_geojson: Path):
    """Test vector.info field extraction."""
    result = await _info(str(tiny_vector_geojson))

    field_names = [field[0] for field in result.fields]
    assert "name" in field_names
    assert "value" in field_names


@pytest.mark.asyncio
async def test_vector_info_bounds(tiny_vector_geojson: Path):
    """Test vector.info bounds extraction."""
    result = await _info(str(tiny_vector_geojson))

    if result.bounds:
        assert len(result.bounds) == 4
        minx, miny, maxx, maxy = result.bounds
        assert minx <= maxx
        assert miny <= maxy
