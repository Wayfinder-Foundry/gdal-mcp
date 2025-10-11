"""Workspace summary generation logic."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import Context

from src.config import get_workspaces
from src.models.workspace_summary import (
    CRSDistribution,
    DatasetCount,
    FormatDistribution,
    SizeStatistics,
    WorkspaceSummary,
)
from src.shared.catalog import scan
from src.shared.metadata.format_detection import read_format_metadata


def generate_workspace_summary(*, ctx: Context | None = None) -> WorkspaceSummary:
    """Generate a comprehensive summary of workspace contents.

    Args:
        ctx: Optional context for logging

    Returns:
        WorkspaceSummary with counts, distributions, and statistics
    """
    workspaces = get_workspaces()

    if ctx:
        ctx.info(f"[workspace_summary] Scanning {len(workspaces)} workspace(s)")

    # Scan all datasets
    all_entries = scan(kind="all", ctx=ctx)

    # Count by type
    raster_count = sum(1 for e in all_entries if e.kind == "raster")
    vector_count = sum(1 for e in all_entries if e.kind == "vector")
    other_count = sum(1 for e in all_entries if e.kind == "other")

    dataset_counts = DatasetCount(
        raster=raster_count,
        vector=vector_count,
        other=other_count,
        total=len(all_entries),
    )

    # Collect CRS information
    crs_counter: Counter[str] = Counter()
    format_counter: Counter[tuple[str, str]] = Counter()  # (format_name, extension)
    total_size = 0
    max_size = 0
    max_file = None

    for entry in all_entries:
        path_str = entry.ref.path
        if not path_str:
            continue

        path = Path(path_str)

        # Size tracking
        if path.exists():
            size = path.stat().st_size
            total_size += size
            if size > max_size:
                max_size = size
                max_file = path_str

        # Get format metadata for raster/vector files
        if entry.kind in ("raster", "vector"):
            try:
                meta = read_format_metadata(path_str)

                # Track CRS
                if "crs" in meta.get("details", {}):
                    crs_str = meta["details"]["crs"]
                    if crs_str:
                        crs_counter[crs_str] += 1

                # Track format
                driver = meta.get("driver")
                if driver:
                    ext = path.suffix.lower()
                    format_counter[(driver, ext)] += 1

            except Exception:
                # Skip files that can't be read
                continue

    # Build CRS distribution
    total_with_crs = sum(crs_counter.values())
    crs_distribution = [
        CRSDistribution(
            crs_code=crs,
            count=count,
            percentage=round((count / total_with_crs * 100), 2) if total_with_crs > 0 else 0.0,
        )
        for crs, count in crs_counter.most_common()
    ]

    # Build format distribution
    total_with_format = sum(format_counter.values())
    format_distribution = [
        FormatDistribution(
            format_name=fmt,
            extension=ext,
            count=count,
            percentage=(
                round((count / total_with_format * 100), 2) if total_with_format > 0 else 0.0
            ),
        )
        for (fmt, ext), count in format_counter.most_common()
    ]

    # Build size statistics
    avg_size = total_size / len(all_entries) if all_entries else 0
    size_statistics = SizeStatistics(
        total_bytes=total_size,
        total_mb=round(total_size / (1024 * 1024), 2),
        total_gb=round(total_size / (1024 * 1024 * 1024), 3),
        average_bytes=round(avg_size, 2),
        largest_file=max_file,
        largest_size_mb=round(max_size / (1024 * 1024), 2) if max_size > 0 else None,
    )

    return WorkspaceSummary(
        workspaces=[str(w) for w in workspaces],
        dataset_counts=dataset_counts,
        crs_distribution=crs_distribution,
        format_distribution=format_distribution,
        size_statistics=size_statistics,
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        metadata={
            "scan_method": "extension_based_classification",
            "hidden_files_included": False,
        },
    )
