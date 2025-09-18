import json
from pathlib import Path
from typing import Tuple

import pytest

import gdal_mcp.utils as utils
from gdal_mcp.app import mcp
from gdal_mcp.tools.info import info as tool_info
from gdal_mcp.tools.convert import convert as tool_convert
from gdal_mcp.tools.raster.reproject import reproject as tool_reproject


@pytest.fixture(autouse=True)
def _noop_gdal_check(monkeypatch):
    # Avoid requiring real GDAL in unit tests
    monkeypatch.setattr(utils, "ensure_gdal_available", lambda: None)


@pytest.mark.asyncio
async def test_info_json_success(monkeypatch):
    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 0, json.dumps({"ok": True}), ""

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    res = await tool_info(path="/tmp/dataset.tif", format="json")
    assert isinstance(res, dict)
    assert res["ok"] is True


@pytest.mark.asyncio
async def test_info_text_success(monkeypatch):
    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 0, "some text", ""

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    res = await tool_info(path="/tmp/dataset.tif", format="text")
    assert res == {"text": "some text"}


@pytest.mark.asyncio
async def test_info_json_nonjson_stdout(monkeypatch):
    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 0, "not json", ""

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    res = await tool_info(path="/tmp/dataset.tif", format="json")
    assert res == {"raw": "not json"}


@pytest.mark.asyncio
async def test_convert_resource_published(tmp_path: Path, monkeypatch):
    # Pre-create the output file so the tool registers it as a resource
    out_path = tmp_path / "converted.tif"
    out_path.write_bytes(b"")

    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 0, "", "conversion ok"

    added = {}

    def fake_add_resource(resource):
        # Capture the resource added by the tool
        added["uri"] = getattr(resource, "uri", None)
        added["name"] = getattr(resource, "name", None)
        return resource

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    monkeypatch.setattr(mcp, "add_resource", fake_add_resource)

    res = await tool_convert(
        input="/tmp/dataset.tif",
        output=str(out_path),
        output_format="GTiff",
    )

    expected_uri = f"file://{out_path.resolve().as_posix()}"
    assert res["output"] == str(out_path.resolve())
    assert res["resource_uri"] == expected_uri
    assert added["uri"] == expected_uri


@pytest.mark.asyncio
async def test_convert_error_raises(monkeypatch):
    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 1, "", "bad convert"

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    with pytest.raises(RuntimeError) as ei:
        await tool_convert(input="/tmp/in.tif", output="/tmp/out.tif")
    assert "gdal convert failed" in str(ei.value)


@pytest.mark.asyncio
async def test_reproject_resource_published(tmp_path: Path, monkeypatch):
    out_path = tmp_path / "reprojected.tif"
    out_path.write_bytes(b"")

    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 0, "", "reproject ok"

    added = {}

    def fake_add_resource(resource):
        added["uri"] = getattr(resource, "uri", None)
        added["name"] = getattr(resource, "name", None)
        return resource

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    monkeypatch.setattr(mcp, "add_resource", fake_add_resource)

    res = await tool_reproject(
        input="/tmp/in.tif",
        output=str(out_path),
        dst_crs="EPSG:4326",
        resampling="near",
    )

    expected_uri = f"file://{out_path.resolve().as_posix()}"
    assert res["output"] == str(out_path.resolve())
    assert res["resource_uri"] == expected_uri
    assert added["uri"] == expected_uri


@pytest.mark.asyncio
async def test_reproject_error_raises(monkeypatch):
    async def fake_run(args, *, env=None) -> Tuple[int, str, str]:
        return 1, "", "bad reproj"

    monkeypatch.setattr(utils, "run_gdal", fake_run)
    with pytest.raises(RuntimeError) as ei:
        await tool_reproject(
            input="/tmp/in.tif",
            output="/tmp/out.tif",
            dst_crs="EPSG:4326",
        )
    assert "gdal raster reproject failed" in str(ei.value)
