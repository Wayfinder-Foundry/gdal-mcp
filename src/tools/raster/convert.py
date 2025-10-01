"""Raster conversion tool using Python-native Rasterio."""
from __future__ import annotations

import os
from pathlib import Path

import rasterio
from rasterio.enums import Resampling

from src.app import mcp
from src.models.common import ResourceRef
from src.models.raster import ConversionOptions, ConversionResult


@mcp.tool(
    name="raster.convert",
    description="Convert raster format with options for compression, tiling, and overviews.",
)
async def raster_convert(
    uri: str,
    output: str,
    options: ConversionOptions | None = None,
) -> ConversionResult:
    """Convert a raster dataset to a new format with specified options.

    Args:
        uri: Path/URI to the source raster dataset.
        output: Path for the output raster file.
        options: Conversion options (driver, compression, tiling, overviews, etc.).

    Returns:
        ConversionResult: Metadata about the converted raster with ResourceRef.
    """
    # Default options if not provided
    if options is None:
        options = ConversionOptions()

    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    with rasterio.Env():
        # Open source dataset
        with rasterio.open(uri) as src:
            # Build output profile from source
            profile = src.profile.copy()

            # Apply conversion options
            profile.update(
                driver=options.driver,
                tiled=options.tiled,
                blockxsize=options.blockxsize,
                blockysize=options.blockysize,
            )

            # Apply compression if specified
            if options.compression:
                profile["compress"] = options.compression.value

            # Apply photometric if specified
            if options.photometric:
                profile["photometric"] = options.photometric

            # Merge additional creation options
            profile.update(options.creation_options)

            # Write output dataset
            with rasterio.open(output, "w", **profile) as dst:
                # Copy all bands
                for band_idx in range(1, src.count + 1):
                    data = src.read(band_idx)
                    dst.write(data, band_idx)

                # Copy tags
                dst.update_tags(**src.tags())

                # Copy per-band tags
                for band_idx in range(1, src.count + 1):
                    dst.update_tags(band_idx, **src.tags(band_idx))

        # Build overviews if requested (must reopen in update mode)
        overviews_built = []
        if options.overviews:
            with rasterio.open(output, "r+") as dst:
                # Map resampling string to Resampling enum
                resampling_map = {
                    "nearest": Resampling.nearest,
                    "bilinear": Resampling.bilinear,
                    "cubic": Resampling.cubic,
                    "average": Resampling.average,
                    "mode": Resampling.mode,
                    "gauss": Resampling.gauss,
                    "lanczos": Resampling.lanczos,
                }
                resampling_method = resampling_map.get(
                    options.overview_resampling.lower(), Resampling.average
                )

                dst.build_overviews(options.overviews, resampling_method)
                overviews_built = options.overviews

        # Get output file size
        output_path = Path(output)
        size_bytes = output_path.stat().st_size

        # Build ResourceRef per ADR-0012
        resource_ref = ResourceRef(
            uri=output_path.as_uri(),
            path=str(output_path.absolute()),
            size=size_bytes,
            driver=options.driver,
            meta={
                "compression": options.compression.value if options.compression else None,
                "tiled": options.tiled,
            },
        )

        # Return ConversionResult per ADR-0017
        return ConversionResult(
            output=resource_ref,
            driver=options.driver,
            compression=options.compression.value if options.compression else None,
            size_bytes=size_bytes,
            overviews_built=overviews_built,
        )
