"""Unit tests for raster tools."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.models.raster.convert import Options as ConvertOptions
from src.models.raster.reproject import Params as ReprojectParams
from src.models.raster.stats import Params as StatsParams
from src.tools.raster.convert import _convert

# Import the core logic functions (not the @mcp.tool wrapped versions)
from src.tools.raster.info import _info
from src.tools.raster.reproject import _reproject
from src.tools.raster.stats import _stats


@pytest.mark.asyncio
async def test_raster_info_basic(tiny_raster_gtiff: Path):
    """Test raster.info on a simple GeoTIFF."""
    result = await _info(str(tiny_raster_gtiff))

    assert result.path == str(tiny_raster_gtiff)
    assert result.driver == "GTiff"
    assert result.crs == "EPSG:4326"
    assert result.width == 10
    assert result.height == 10
    assert result.count == 1
    assert result.dtype == "uint8"
    assert result.nodata == 255
    assert len(result.transform) == 6
    assert len(result.bounds) == 4


@pytest.mark.asyncio
async def test_raster_info_rgb(tiny_raster_rgb: Path):
    """Test raster.info on a 3-band RGB raster."""
    result = await _info(str(tiny_raster_rgb))

    assert result.count == 3
    assert result.width == 10
    assert result.height == 10


@pytest.mark.asyncio
async def test_raster_convert_basic(tiny_raster_gtiff: Path, test_data_dir: Path):
    """Test raster.convert with default options."""
    output_path = test_data_dir / "converted.tif"

    result = await _convert(
        uri=str(tiny_raster_gtiff),
        output=str(output_path),
    )

    assert result.driver == "GTiff"
    assert result.size_bytes > 0
    assert output_path.exists()
    assert result.output.path == str(output_path.absolute())


@pytest.mark.asyncio
async def test_raster_convert_with_compression(tiny_raster_gtiff: Path, test_data_dir: Path):
    """Test raster.convert with LZW compression."""
    output_path = test_data_dir / "converted_lzw.tif"

    options = ConvertOptions(
        driver="GTiff",
        compression="lzw",
        tiled=True,
    )

    result = await _convert(
        uri=str(tiny_raster_gtiff),
        output=str(output_path),
        options=options,
    )

    assert result.compression == "lzw"
    assert output_path.exists()


@pytest.mark.asyncio
async def test_raster_convert_with_overviews(tiny_raster_gtiff: Path, test_data_dir: Path):
    """Test raster.convert with overview building."""
    output_path = test_data_dir / "converted_overviews.tif"

    options = ConvertOptions(
        overviews=[2, 4],
        overview_resampling="average",
    )

    result = await _convert(
        uri=str(tiny_raster_gtiff),
        output=str(output_path),
        options=options,
    )

    assert result.overviews_built == [2, 4]


@pytest.mark.asyncio
async def test_raster_reproject_basic(tiny_raster_gtiff: Path, test_data_dir: Path):
    """Test raster.reproject to Web Mercator."""
    output_path = test_data_dir / "reprojected.tif"

    params = ReprojectParams(
        dst_crs="EPSG:3857",
        resampling="nearest",
    )

    result = await _reproject(
        uri=str(tiny_raster_gtiff),
        output=str(output_path),
        params=params,
    )

    assert result.dst_crs == "EPSG:3857"
    assert result.src_crs == "EPSG:4326"
    assert result.resampling == "nearest"
    assert result.width > 0
    assert result.height > 0
    assert output_path.exists()


@pytest.mark.asyncio
async def test_raster_reproject_with_resolution(tiny_raster_gtiff: Path, test_data_dir: Path):
    """Test raster.reproject with explicit resolution."""
    output_path = test_data_dir / "reprojected_res.tif"

    params = ReprojectParams(
        dst_crs="EPSG:4326",
        resampling="bilinear",
        resolution=(0.5, 0.5),  # Half-degree pixels
    )

    result = await _reproject(
        uri=str(tiny_raster_gtiff),
        output=str(output_path),
        params=params,
    )

    assert result.dst_crs == "EPSG:4326"
    assert output_path.exists()


@pytest.mark.asyncio
async def test_raster_stats_basic(tiny_raster_gtiff: Path):
    """Test raster.stats on a simple raster."""
    result = await _stats(str(tiny_raster_gtiff))

    assert result.path == str(tiny_raster_gtiff)
    assert result.total_pixels == 100
    assert len(result.band_stats) == 1

    band_stat = result.band_stats[0]
    assert band_stat.band == 1
    assert band_stat.min is not None
    assert band_stat.max is not None
    assert band_stat.mean is not None
    assert band_stat.std is not None
    assert band_stat.valid_count > 0


@pytest.mark.asyncio
async def test_raster_stats_with_nodata(tiny_raster_with_nodata: Path):
    """Test raster.stats with nodata handling."""
    result = await _stats(str(tiny_raster_with_nodata))

    band_stat = result.band_stats[0]
    assert band_stat.nodata_count == 4  # Top-left 2x2 corner
    assert band_stat.valid_count == 96


@pytest.mark.asyncio
async def test_raster_stats_with_histogram(tiny_raster_gtiff: Path):
    """Test raster.stats with histogram generation."""
    params = StatsParams(
        include_histogram=True,
        histogram_bins=10,
    )

    result = await _stats(str(tiny_raster_gtiff), params)

    band_stat = result.band_stats[0]
    assert len(band_stat.histogram) == 10
    assert all(bin.count >= 0 for bin in band_stat.histogram)


@pytest.mark.asyncio
async def test_raster_stats_multiple_bands(tiny_raster_rgb: Path):
    """Test raster.stats on multi-band raster."""
    params = StatsParams(
        bands=[1, 2, 3],
    )

    result = await _stats(str(tiny_raster_rgb), params)

    assert len(result.band_stats) == 3
    assert result.band_stats[0].band == 1
    assert result.band_stats[1].band == 2
    assert result.band_stats[2].band == 3


@pytest.mark.asyncio
async def test_raster_stats_percentiles(tiny_raster_gtiff: Path):
    """Test raster.stats with custom percentiles."""
    params = StatsParams(
        percentiles=[10.0, 50.0, 90.0],
    )

    result = await _stats(str(tiny_raster_gtiff), params)

    band_stat = result.band_stats[0]
    assert band_stat.median is not None
    # Custom percentiles computed internally
