import pytest
import subprocess

import server.gdal_tools as gt

from pathlib import Path

# --- Helper fixtures ---

class DummyCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

@pytest.fixture()
def tmp_file(tmp_path):
    f = tmp_path / "sample.tif"
    f.write_bytes(b"GTIFFPLACEHOLDER")
    return f

@pytest.fixture()
def mock_run(monkeypatch):
    calls = []

    def _run(cmd, capture_output=True, text=True, timeout=0, check=False):
        calls.append(cmd)
        tool = Path(cmd[0]).name
        if tool == "gdalinfo":
            if "--version" in cmd:
                return DummyCompleted(0, "GDAL 3.9.0, released 2025/01/01", "")
            if "--formats" in cmd:
                return DummyCompleted(0, "GTiff (rw+) GeoTIFF\nPNG (rw+) Portable Network Graphics", "")
            # dataset info
            return DummyCompleted(0, "Driver: GTiff/GeoTIFF\nSize is 10, 10", "")
        if tool == "gdal_translate":
            # succeed and create output file if last arg looks like path
            out_path = cmd[-1]
            Path(out_path).write_bytes(b"translated")
            return DummyCompleted(0, "Translation successful", "")
        if tool == "gdalwarp":
            out_path = cmd[-1]
            Path(out_path).write_bytes(b"warped")
            return DummyCompleted(0, "Warp successful", "")
        if tool == "gdalbuildvrt":
            out_path = cmd[cmd.index("gdalbuildvrt") + 1] if "gdalbuildvrt" in cmd else cmd[1]
            # Actually the CLI is gdalbuildvrt <dst> <src...>; our wrapper builds list accordingly
            # pick last path with .vrt extension
            for c in cmd:
                if str(c).endswith('.vrt'):
                    Path(c).write_text('<VRTDataset/>')
            return DummyCompleted(0, "VRT build successful", "")
        return DummyCompleted(1, "", "Unknown tool")

    monkeypatch.setattr(subprocess, "run", _run)
    return calls

# --- Tests for internal helpers ---

def test_validate_file_path(tmp_file):
    assert gt._validate_file_path(tmp_file) is True
    assert gt._validate_file_path(tmp_file.parent / "missing.tif") is False

def test_output_path(tmp_file):
    p = gt._output_path(tmp_file, suffix="_c", extension=".dat")
    assert p.endswith("_c.dat")

# --- gdalinfo wrapper ---

def test_gdalinfo_success(tmp_file, mock_run):
    out = gt.gdalinfo(str(tmp_file))
    assert "Driver: GTiff" in out


def test_gdalinfo_missing():
    out = gt.gdalinfo("/no/such/file.tif")
    assert out.startswith("Error:")

# --- gdal_translate ---

def test_gdal_translate_success(tmp_file, mock_run, tmp_path):
    dst = tmp_path / "out.tif"
    out = gt.gdal_translate(str(tmp_file), str(dst), output_format="GTiff", bands=[1])
    assert "Successfully converted" in out
    assert dst.exists()


def test_gdal_translate_bad_format(tmp_file):
    out = gt.gdal_translate(str(tmp_file), output_format="BADFMT")
    assert "Invalid output format" in out

# --- gdalwarp ---

def test_gdalwarp_success(tmp_file, mock_run, tmp_path):
    dst = tmp_path / "warp.tif"
    out = gt.gdalwarp([str(tmp_file)], str(dst), target_epsg=3857, resampling="near")
    assert "Successfully warped" in out
    assert dst.exists()


def test_gdalwarp_invalid_resample(tmp_file):
    out = gt.gdalwarp([str(tmp_file)], resampling="bogus")
    assert "Invalid resampling" in out

# --- gdalbuildvrt ---

def test_gdalbuildvrt_success(tmp_file, mock_run, tmp_path):
    other = tmp_path / "other.tif"
    other.write_bytes(b"GTIFFPLACEHOLDER")
    dst_vrt = tmp_path / "mosaic.vrt"
    out = gt.gdalbuildvrt([str(tmp_file), str(other)], str(dst_vrt))
    assert "Successfully created VRT" in out
    assert dst_vrt.exists()


def test_gdalbuildvrt_missing_src():
    out = gt.gdalbuildvrt([])
    assert out.startswith("Error: No source datasets")

# --- check_gdal_installation & list_gdal_formats ---

def test_check_gdal_installation(mock_run):
    out = gt.check_gdal_installation()
    assert out.startswith("GDAL is installed")


def test_list_gdal_formats(mock_run):
    out = gt.list_gdal_formats()
    assert "GTiff" in out and "PNG" in out

# --- command helper error paths ---

def test_command_timeout(monkeypatch):
    class Timeout(Exception):
        pass
    def raise_timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd=['gdalinfo'], timeout=1)
    monkeypatch.setattr(subprocess, 'run', raise_timeout)
    res = gt.command(['gdalinfo'])
    assert res['success'] is False and 'timed out' in res['error']


def test_command_not_found(monkeypatch):
    def raise_nf(*a, **k):
        raise FileNotFoundError('gdalinfo')
    monkeypatch.setattr(subprocess, 'run', raise_nf)
    res = gt.command(['gdalinfo'])
    assert res['success'] is False and 'Command not found' in res['error']
