"""Raster reprojection tool using Python-native Rasterio."""

from __future__ import annotations

import rasterio
from fastmcp import Context
from fastmcp.exceptions import ToolError
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject as rio_reproject

from src.app import mcp
from src.config import resolve_path
from src.models.raster.reproject import Params, Result
from src.models.resourceref import ResourceRef


async def _reproject(
    uri: str,
    output: str,
    params: Params,
    ctx: Context | None = None,
) -> Result:
    """Core logic: Reproject a raster dataset to a new CRS.

    Args:
        uri: Path/URI to the source raster dataset (relative or absolute).
        output: Path for the output raster file (relative or absolute).
        params: Reprojection parameters (dst_crs, resampling, resolution, etc.).
        ctx: Optional MCP context for logging and progress reporting.

    Returns:
        Result: Metadata about the reprojected raster with ResourceRef.

    Raises:
        ToolError: If raster cannot be opened or reprojection fails.
    """
    # Resolve paths to absolute
    uri_path = str(resolve_path(uri))
    output_path = resolve_path(output)

    if ctx:
        await ctx.info("📂 Opening source raster: " + uri_path)
        await ctx.debug("Target CRS: " + params.dst_crs + ", Resampling: " + params.resampling)

    # Per ADR-0013: wrap in rasterio.Env for per-request config isolation
    try:
        with rasterio.Env():
            with rasterio.open(uri_path) as src:
                # Determine source CRS (use override if provided)
                src_crs = params.src_crs if params.src_crs else src.crs
                if src_crs is None:
                    raise ToolError(
                        "Source CRS not found in raster '" + uri + "' and not provided in params. "
                        "Please specify src_crs parameter with the coordinate system "
                        "(e.g., 'EPSG:4326')."
                    )

                if ctx:
                    await ctx.info(
                        "✓ Source: "
                        + str(src_crs)
                        + ", "
                        + str(src.width)
                        + "x"
                        + str(src.height)
                        + ", "
                        + str(src.count)
                        + " bands, "
                        + (src.dtypes[0] if src.dtypes else "unknown")
                    )
                    await ctx.report_progress(0, 100)

                # Map resampling string to Rasterio Resampling enum
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
                # params.resampling is now a string literal
                resampling_method = resampling_map.get(params.resampling)
                if resampling_method is None:
                    raise ToolError(
                        f"Invalid resampling method: {params.resampling}. "
                        f"Must be one of: {', '.join(resampling_map.keys())}"
                    )

                # Calculate destination transform and dimensions
                if ctx:
                    await ctx.info("📐 Calculating output transform and dimensions...")

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

                if ctx:
                    await ctx.info(
                        "✓ Output: "
                        + params.dst_crs
                        + ", "
                        + str(dst_width)
                        + "x"
                        + str(dst_height)
                        + " pixels"
                    )
                    await ctx.report_progress(10, 100)

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

                if ctx:
                    await ctx.info("📝 Writing reprojected output: " + str(output_path))

                # Write reprojected dataset
                with rasterio.open(str(output_path), "w", **profile) as dst:
                    for band_idx in range(1, src.count + 1):
                        # Progress: 10% setup, 80% reprojection (distributed), 10% finalize
                        progress_start = 10 + int(((band_idx - 1) / src.count) * 80)

                        if ctx:
                            await ctx.report_progress(progress_start, 100)
                            await ctx.debug(
                                "Reprojecting band "
                                + str(band_idx)
                                + "/"
                                + str(src.count)
                                + " "
                                + "("
                                + params.resampling
                                + " resampling)"
                            )

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

                if ctx:
                    await ctx.report_progress(90, 100)

            # Get output file size
            size_bytes = output_path.stat().st_size

            # Calculate output bounds in destination CRS
            with rasterio.open(str(output_path)) as dst:
                dst_bounds = dst.bounds

            if ctx:
                await ctx.report_progress(100, 100)
                await ctx.info(
                    "✓ Reprojection complete: "
                    + str(output_path)
                    + " ("
                    + str(size_bytes)
                    + " bytes)"
                )

            # Build ResourceRef per ADR-0012
            resource_ref = ResourceRef(
                uri=output_path.as_uri(),
                path=str(output_path.absolute()),
                size=size_bytes,
                driver=profile["driver"],
                meta={
                    "src_crs": str(src_crs),
                    "dst_crs": params.dst_crs,
                    "resampling": params.resampling,
                },
            )

            # Return ReprojectionResult per ADR-0017
            return Result(
                output=resource_ref,
                src_crs=str(src_crs),
                dst_crs=params.dst_crs,
                resampling=params.resampling,
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
                bounds=[
                    dst_bounds.left,
                    dst_bounds.bottom,
                    dst_bounds.right,
                    dst_bounds.top,
                ],
            )

    except rasterio.errors.RasterioIOError as e:
        raise ToolError(
            "Cannot open source raster at '" + uri + "'. "
            "Please ensure: (1) file exists, (2) file is a valid raster format. "
            "Supported formats: GeoTIFF, COG, PNG, JPEG, NetCDF, HDF5. "
            "Original error: " + str(e)
        ) from e
    except rasterio.errors.CRSError as e:
        raise ToolError(
            "Invalid CRS specification. "
            "Please use standard CRS formats like 'EPSG:3857', 'EPSG:4326', "
            "or WKT/PROJ strings. "
            "Original error: " + str(e)
        ) from e
    except PermissionError as e:
        raise ToolError(
            "Permission denied writing to '" + output + "'. "
            "Please ensure: (1) output directory exists, "
            "(2) you have write permissions to the directory."
        ) from e
    except MemoryError as e:
        raise ToolError(
            "Out of memory during reprojection. "
            "Try: (1) specifying smaller output dimensions with width/height, "
            "(2) processing the raster in tiles, or (3) using a system with more RAM."
        ) from e
    except Exception as e:
        raise ToolError("Unexpected error during reprojection: " + str(e)) from e


@mcp.tool(
    name="raster_reproject",
    description=(
        "Reproject raster to new coordinate reference system with explicit resampling "
        "method (ADR-0011 requirement). "
        "USE WHEN: Coordinate system doesn't match target projection OR "
        "data needs different spatial reference for analysis, overlay, or web serving. "
        "Common scenarios: convert lat/lon (EPSG:4326) to Web Mercator (EPSG:3857) for web maps, "
        "transform to local UTM zone for accurate area/distance calculations, or align multiple "
        "rasters to common projection for analysis. "
        "REQUIRES: uri (source raster path), output (destination file path), "
        "dst_crs (e.g. 'EPSG:3857', 'EPSG:4326', 'EPSG:32610'), "
        "resampling (nearest for categorical data, bilinear/cubic for continuous data). "
        "OPTIONAL: src_crs (override source CRS if missing/incorrect), "
        "resolution (target pixel size as [x, y] list in destination units),"
        "width/height (explicit output dimensions in pixels), "
        "bounds (crop to extent in destination CRS as [left, bottom, right, top]),"
        "nodata (override nodata value for output). "
        "OUTPUT: ReprojectionResult with ResourceRef (output file URI/path/size/metadata), "
        "src_crs used, dst_crs, resampling method, output transform (6-element affine), "
        "width/height in pixels, and bounds in destination CRS. "
        "SIDE EFFECTS: Creates new file at output path. "
        "NOTE: Resampling method is REQUIRED per ADR-0011 to prevent unintentional data "
        "corruption (no defaults). Choose carefully: nearest preserves exact values but creates "
        "blocky appearance, bilinear/cubic create smooth output but may introduce new values."
    ),
)
async def reproject(
    uri: str,
    output: str,
    dst_crs: str,
    resampling: str,
    src_crs: str | None = None,
    resolution: list[float] | None = None,
    width: int | None = None,
    height: int | None = None,
    bounds: list[float] | None = None,
    nodata: float | None = None,
    ctx: Context | None = None,
) -> Result:
    """MCP tool wrapper for raster reprojection with flattened parameters.

    Includes reflection preflight for CRS selection and resampling method justification.
    """
    # Build Params object from flattened parameters
    params = Params(
        dst_crs=dst_crs,
        resampling=resampling,  # type: ignore[arg-type]
        src_crs=src_crs,
        resolution=resolution,
        width=width,
        height=height,
        bounds=bounds,
        nodata=nodata,
    )
    return await _reproject(uri, output, params, ctx)
