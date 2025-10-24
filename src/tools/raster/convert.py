"""Raster conversion tool using Python-native Rasterio."""

from __future__ import annotations

import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError
from rasterio.enums import Resampling

from src.app import mcp
from src.config import resolve_path
from src.models.raster.convert import Options, Result
from src.models.resourceref import ResourceRef


async def _convert(
    uri: str,
    output: str,
    options: Options | None = None,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Convert a raster dataset to a new format.

    Args:
        uri: Path/URI to the source raster dataset (relative or absolute).
        output: Path for the output raster file (relative or absolute).
        options: Conversion options (driver, compression, tiling, overviews, etc.).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the converted raster with ResourceRef.

    Raises:
        ToolError: If raster cannot be opened or conversion fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    # Default options if not provided
    if options is None:
        options = Options()

    if ctx:
        await ctx.info(f"📂 Opening source raster: {uri_path}")
        await ctx.debug(
            f"Conversion target: driver={options.driver}, "
            f"compression={options.compression}, tiled={options.tiled}"
        )

    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    try:
        with rasterio.Env():
            # Open source dataset
            with rasterio.open(uri_path) as src:
                if ctx:
                    await ctx.info(
                        f"✓ Source: {src.driver}, {src.width}x{src.height}, "
                        f"{src.count} bands, {src.dtypes[0] if src.dtypes else 'unknown'}"
                    )
                    await ctx.report_progress(0, 100)

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
                    # compression is now a string literal
                    profile["compress"] = options.compression
                    if ctx:
                        await ctx.debug(f"Applying compression: {options.compression}")

                # Apply photometric if specified
                if options.photometric:
                    profile["photometric"] = options.photometric

                # Merge additional creation options
                profile.update(options.creation_options)

                if ctx:
                    await ctx.info(f"📝 Writing output: {output_path}")

                # Write output dataset
                with rasterio.open(str(output_path), "w", **profile) as dst:
                    # Copy all bands with progress reporting
                    for band_idx in range(1, src.count + 1):
                        if ctx:
                            progress = int((band_idx / src.count) * 80)  # Reserve 20% for overviews
                            await ctx.report_progress(progress, 100)
                            await ctx.debug(f"Copying band {band_idx}/{src.count}")

                        data = src.read(band_idx)
                        dst.write(data, band_idx)

                    # Copy tags
                    dst.update_tags(**src.tags())

                    # Copy per-band tags
                    for band_idx in range(1, src.count + 1):
                        dst.update_tags(band_idx, **src.tags(band_idx))

            if ctx:
                await ctx.report_progress(80, 100)

            # Build overviews if requested (must reopen in update mode)
            overviews_built = []
            if options.overviews:
                if ctx:
                    await ctx.info(f"🔨 Building overviews: {options.overviews}")

                with rasterio.open(str(output_path), "r+") as dst:
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

                if ctx:
                    await ctx.debug(f"✓ Overviews built: {overviews_built}")

            # Get output file size
            size_bytes = output_path.stat().st_size

            if ctx:
                await ctx.report_progress(100, 100)
                await ctx.info(f"✓ Conversion complete: {output} ({size_bytes:,} bytes)")

            # Build ResourceRef per ADR-0012
            resource_ref = ResourceRef(
                uri=output_path.as_uri(),
                path=str(output_path.absolute()),
                size=size_bytes,
                driver=options.driver,
                meta={
                    "compression": options.compression,
                    "tiled": options.tiled,
                },
            )

            # Return ConversionResult per ADR-0017
            return Result(
                output=resource_ref,
                driver=options.driver,
                compression=options.compression,
                size_bytes=size_bytes,
                overviews_built=overviews_built,
            )

    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            f"Cannot open source raster at '{uri}'. "
            f"Please ensure: (1) file exists, (2) file is a valid raster format. "
            f"Supported formats: GeoTIFF, COG, PNG, JPEG, NetCDF, HDF5. "
            f"Original error: {str(e)}"
        ) from e
    except PermissionError as e:
        raise ToolError(
            f"Permission denied writing to '{output}'. "
            f"Please ensure: (1) output directory exists, "
            f"(2) you have write permissions to the directory."
        ) from e
    except OSError as e:
        raise ToolError(f"Failed to write output file '{output}': {str(e)}") from e
    except Exception as e:
        raise ToolError(f"Unexpected error during conversion: {str(e)}") from e


@mcp.tool(
    name="raster_convert",
    description=(
        "Convert raster format with compression, tiling, and overview generation. "
        "USE WHEN: Need to change format (e.g. GeoTIFF to COG), apply compression "
        "to reduce file size, create tiled output for performance, or build overviews "
        "for faster display at multiple scales. Common use cases: create Cloud-Optimized "
        "GeoTIFFs (COG) for web serving, compress large rasters, or prepare data for GIS software. "
        "REQUIRES: uri (source raster path), output (destination file path). "
        "OPTIONAL: options (ConversionOptions) with driver (GTiff, COG, PNG, JPEG, etc.), "
        "compression (lzw, deflate, zstd, jpeg, packbits, none), tiled (bool, default True), "
        "blockxsize/blockysize (tile dimensions, default 256x256), photometric (RGB, YCBCR), "
        "overviews (list of levels like [2, 4, 8, 16]), overview_resampling "
        "(nearest, bilinear, cubic, average, mode), "
        "creation_options (dict of driver-specific options). "
        "OUTPUT: ConversionResult with ResourceRef "
        "(output file URI, path, size, driver, metadata), "
        "driver name, compression method used, size_bytes, and overviews_built list. "
        "SIDE EFFECTS: Creates new file at output path. "
        "NOTE: COG driver automatically creates optimized cloud-friendly GeoTIFFs."
    ),
)
async def convert(
    uri: str,
    output: str,
    options: Options | None = None,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for raster conversion."""
    return await _convert(uri, output, options, ctx)
