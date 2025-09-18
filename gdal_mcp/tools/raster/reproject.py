from __future__ import annotations

from typing import Dict, List, Optional
from pathlib import Path
from fastmcp.resources import FileResource

from gdal_mcp.app import mcp
from gdal_mcp.utils import run_gdal


def _co_flags(creation_options: Optional[Dict[str, str]]) -> List[str]:
    flags: List[str] = []
    if creation_options:
        for k, v in creation_options.items():
            flags += ["--creation-option", f"{k}={v}"]
    return flags


@mcp.tool
async def reproject(
    input: str,
    output: str,
    dst_crs: str,
    src_crs: Optional[str] = None,
    resampling: Optional[str] = None,
    resolution: Optional[str] = None,
    size: Optional[str] = None,
    bbox: Optional[str] = None,
    bbox_crs: Optional[str] = None,
    overwrite: bool = True,
    creation_options: Optional[Dict[str, str]] = None,
    warp_options: Optional[Dict[str, str]] = None,
    transform_options: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None,
) -> Dict:
    """
    Reproject a raster using 'gdal raster reproject'.

    dst_crs: e.g., 'EPSG:4326'
    resolution: '<xres>,<yres>'
    size: '<width>,<height>' (mutually exclusive with resolution)
    bbox: '<xmin>,<ymin>,<xmax>,<ymax>' (in --bbox-crs if provided, else dst_crs)
    """
    args: List[str] = [
        "gdal",
        "raster",
        "reproject",
        input,
        output,
        "--dst-crs",
        dst_crs,
    ]
    if src_crs:
        args += ["--src-crs", src_crs]
    if resampling:
        args += ["--resampling", resampling]
    if resolution:
        args += ["--resolution", resolution]
    if size:
        args += ["--size", size]
    if bbox:
        args += ["--bbox", bbox]
    if bbox_crs:
        args += ["--bbox-crs", bbox_crs]
    if overwrite:
        args += ["--overwrite"]
    args += _co_flags(creation_options)
    if warp_options:
        for k, v in warp_options.items():
            args += ["--warp-option", f"{k}={v}"]
    if transform_options:
        for k, v in transform_options.items():
            args += ["--transform-option", f"{k}={v}"]
    if extra_args:
        args += list(extra_args)
    code, out, err = await run_gdal(args)
    if code != 0:
        raise RuntimeError(f"gdal raster reproject failed: {err.strip() or out.strip()}")
    # Publish output as a resource if the file exists
    out_abs: Optional[Path] = None
    resource_uri: Optional[str] = None
    try:
        out_abs = Path(output).resolve()
        if out_abs.exists():
            resource_uri = f"file://{out_abs.as_posix()}"
            mcp.add_resource(
                FileResource(
                    uri=resource_uri,
                    path=out_abs,
                    name=out_abs.name,
                    description="Output from gdal raster reproject",
                )
            )
    except Exception:
        # Best-effort; do not fail tool if resource registration fails
        pass
    return {"output": str(out_abs) if out_abs else output, "resource_uri": resource_uri, "stderr": err.strip()}