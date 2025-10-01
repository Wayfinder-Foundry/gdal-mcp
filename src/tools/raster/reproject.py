"""Raster reprojection tool using Python-native Rasterio."""
from __future__ import annotations

from pathlib import Path

import rasterio
from rasterio.warp import calculate_default_transform, reproject as rio_reproject
from rasterio.enums import Resampling

from src.app import mcp
from src.models.common import ResourceRef
from src.models.raster import ReprojectionParams, ReprojectionResult


@mcp.tool(
    name="raster.reproject",
    description="Reproject a raster to a new CRS with explicit resampling method.",
)
async def raster_reproject(
    uri: str,
    output: str,
    params: ReprojectionParams,
) -> ReprojectionResult:
    """Reproject a raster dataset to a new coordinate reference system.

    Args:
        uri: Path/URI to the source raster dataset.
        output: Path for the output raster file.
        params: Reprojection parameters (dst_crs, resampling, resolution, etc.).

    Returns:
        ReprojectionResult: Metadata about the reprojected raster with ResourceRef.
    """
    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    with rasterio.Env():
        with rasterio.open(uri) as src:
            # Determine source CRS (use override if provided)
            src_crs = params.src_crs if params.src_crs else src.crs
            if src_crs is None:
                raise ValueError("Source CRS not found and not provided in params")

            # Map resampling enum to Rasterio Resampling
            resampling_map = {
                "nearest": Resampling.nearest,
                "bilinear": Resampling.bilinear,
                "cubic": Resampling.cubic,
                "cubic_spline": Resampling.cubic_spline,
                "lanczos": Resampling.lanczos,
                "average": Resampling.average,
                "mode": Resampling.mode,
                "gauss": Resampling.gauss,
            }
            resampling_method = resampling_map.get(
                params.resampling.value, Resampling.nearest
            )

            # Calculate destination transform and dimensions
            if params.resolution:
                # Use specified resolution
                dst_transform, dst_width, dst_height = calculate_default_transform(
                    src_crs,
                    params.dst_crs,
                    src.width,
                    src.height,
                    *src.bounds,
                    resolution=params.resolution,
                )
            elif params.width and params.height:
                # Use specified dimensions
                dst_transform, _, _ = calculate_default_transform(
                    src_crs,
                    params.dst_crs,
                    src.width,
                    src.height,
                    *src.bounds,
                )
                dst_width = params.width
                dst_height = params.height
            else:
                # Auto-calculate optimal transform and dimensions
                dst_transform, dst_width, dst_height = calculate_default_transform(
                    src_crs,
                    params.dst_crs,
                    src.width,
                    src.height,
                    *src.bounds,
                )

            # Build output profile
            profile = src.profile.copy()
            profile.update(
                {
                    "crs": params.dst_crs,
                    "transform": dst_transform,
                    "width": dst_width,
                    "height": dst_height,
                }
            )

            # Update nodata if specified
            if params.nodata is not None:
                profile["nodata"] = params.nodata

            # Write reprojected dataset
            with rasterio.open(output, "w", **profile) as dst:
                for band_idx in range(1, src.count + 1):
                    rio_reproject(
                        source=rasterio.band(src, band_idx),
                        destination=rasterio.band(dst, band_idx),
                        src_transform=src.transform,
                        src_crs=src_crs,
                        dst_transform=dst_transform,
                        dst_crs=params.dst_crs,
                        resampling=resampling_method,
                    )

                # Copy tags
                dst.update_tags(**src.tags())

        # Get output file size
        output_path = Path(output)
        size_bytes = output_path.stat().st_size

        # Calculate output bounds in destination CRS
        with rasterio.open(output) as dst:
            dst_bounds = dst.bounds

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver=profile["driver"],
            meta={
                "src_crs": str(src_crs),
                "dst_crs": params.dst_crs,
                "resampling": params.resampling.value,
            },
        )

        # Return ReprojectionResult per ADR-0017
        return ReprojectionResult(
            output=resource_ref,
            src_crs=str(src_crs),
            dst_crs=params.dst_crs,
            resampling=params.resampling.value,
            transform=[
                dst_transform.a,
                dst_transform.b,
                dst_transform.c,
                dst_transform.d,
                dst_transform.e,
                dst_transform.f,
            ],
            width=dst_width,
            height=dst_height,
            bounds=(dst_bounds.left, dst_bounds.bottom, dst_bounds.right, dst_bounds.top),
        )
