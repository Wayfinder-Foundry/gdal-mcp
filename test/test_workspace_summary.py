"""Tests for workspace summary resource."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from src.config import reset_workspaces_cache
from src.shared.catalog import clear_cache, generate_workspace_summary


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


def test_workspace_summary_empty(workspace: Path) -> None:
    """Verify summary works for empty workspace."""
    summary = generate_workspace_summary()

    assert summary.dataset_counts.total == 0
    assert summary.dataset_counts.raster == 0
    assert summary.dataset_counts.vector == 0
    assert summary.dataset_counts.other == 0
    assert len(summary.crs_distribution) == 0
    assert len(summary.format_distribution) == 0
    assert summary.size_statistics.total_bytes == 0


def test_workspace_summary_counts(workspace: Path) -> None:
    """Verify summary counts datasets by type."""
    # Create test files
    _touch(workspace / "data" / "dem.tif")
    _touch(workspace / "data" / "ortho.tif")
    _touch(workspace / "data" / "roads.geojson")
    _touch(workspace / "notes" / "readme.txt")

    summary = generate_workspace_summary()

    assert summary.dataset_counts.total == 4
    assert summary.dataset_counts.raster == 2
    assert summary.dataset_counts.vector == 1
    assert summary.dataset_counts.other == 1


def test_workspace_summary_size_statistics(workspace: Path) -> None:
    """Verify summary calculates size statistics."""
    # Create files with known sizes
    file1 = workspace / "small.tif"
    file2 = workspace / "large.tif"

    _touch(file1)
    _touch(file2)

    # Write some data
    file1.write_bytes(b"x" * 1024)  # 1 KB
    file2.write_bytes(b"x" * (1024 * 1024))  # 1 MB

    summary = generate_workspace_summary()

    assert summary.size_statistics.total_bytes == 1024 + (1024 * 1024)
    assert summary.size_statistics.total_mb >= 1.0
    assert summary.size_statistics.average_bytes > 0
    assert summary.size_statistics.largest_file == str(file2.resolve())
    assert summary.size_statistics.largest_size_mb == 1.0


def test_workspace_summary_format_distribution(workspace: Path) -> None:
    """Verify summary tracks format distribution."""
    _touch(workspace / "file1.tif")
    _touch(workspace / "file2.tif")
    _touch(workspace / "file3.geojson")

    summary = generate_workspace_summary()

    # Should have 2 TIF files and 1 GeoJSON
    assert summary.dataset_counts.total == 3

    # Format distribution should reflect the mix
    # (Note: actual format detection requires valid raster/vector files,
    # so with empty files we won't get format_distribution populated)
    # This test just verifies the structure is present
    assert isinstance(summary.format_distribution, list)


def test_workspace_summary_timestamp(workspace: Path) -> None:
    """Verify summary includes scan timestamp."""
    summary = generate_workspace_summary()

    assert summary.scan_timestamp
    assert "T" in summary.scan_timestamp  # ISO 8601 format
    assert summary.metadata["scan_method"] == "extension_based_classification"


def test_workspace_summary_workspaces_list(workspace: Path) -> None:
    """Verify summary lists configured workspaces."""
    summary = generate_workspace_summary()

    assert len(summary.workspaces) == 1
    assert str(workspace) in summary.workspaces
