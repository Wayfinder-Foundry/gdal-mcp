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
async def convert(
    input: str,
    output: str,
    output_format: Optional[str] = None,
    overwrite: bool = True,
    creation_options: Optional[Dict[str, str]] = None,
    extra_args: Optional[List[str]] = None,
) -> Dict:
    """
    Convert a dataset using the unified 'gdal convert' command.

    - output_format: driver short name (e.g., GTiff, COG, GPKG)
    - creation_options: driver-specific creation options
    - extra_args: additional CLI args passed through verbatim
    """
    args: List[str] = ["gdal", "convert", input, output]
    if output_format:
        args += ["--output-format", output_format]
    if overwrite:
        args += ["--overwrite"]
    args += _co_flags(creation_options)
    if extra_args:
        args += list(extra_args)
    code, out, err = await run_gdal(args)
    if code != 0:
        raise RuntimeError(f"gdal convert failed: {err.strip() or out.strip()}")
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
                    description="Output from gdal convert",
                )
            )
    except Exception:
        # Resource publication is best-effort; do not fail the tool on errors here
        pass
    return {"output": str(out_abs) if out_abs else output, "resource_uri": resource_uri, "stderr": err.strip()}