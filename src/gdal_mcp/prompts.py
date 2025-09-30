from __future__ import annotations

from typing import Optional

from gdal_mcp.app import mcp


@mcp.prompt(name="gdal_task", description="Guide the model to choose and call GDAL MCP tools to achieve a goal.")
def gdal_task(
    goal: str,
    input_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """Render guidance for using GDAL MCP tools to accomplish a task.

    goal: Natural language goal (e.g., "Inspect a GeoTIFF and convert to COG")
    input_path: Optional input path hint
    output_path: Optional output path hint
    """
    guidance = f"""
You are a GDAL assistant operating against an MCP server that exposes selected GDAL 3.11 unified CLI commands as tools.

Goal: {goal}

Available tools (names and arguments):
- info(path: str, format: 'json'|'text' = 'json')
- convert(input: str, output: str, output_format?: str, overwrite: bool = true, creation_options?: dict[str,str], extra_args?: list[str])
- reproject(input: str, output: str, dst_crs: str, src_crs?: str, resampling?: str, resolution?: str, size?: str, bbox?: str, bbox_crs?: str, overwrite: bool = true, creation_options?: dict[str,str], warp_options?: dict[str,str], transform_options?: dict[str,str], extra_args?: list[str])

Guidance:
1) Prefer info(format='json') for inspection and schema understanding.
2) For conversion, be explicit about output_format (e.g., 'GTiff', 'COG') and pass creation options where relevant (e.g., TILED=YES, COMPRESS=ZSTD).
3) For reproject, provide dst_crs (e.g., 'EPSG:4326') and optionally resampling/resolution/size; do not pass both resolution and size.
4) File-producing tools will return a resource_uri (file://...) you can read via the Resources API.
5) Always request user approval before tool execution (host enforces confirmation).

Inputs (hints):
- input_path: {input_path or 'N/A'}
- output_path: {output_path or 'N/A'}

Produce the next step as a concrete MCP tool call proposal:
- name: one of [info, convert, reproject]
- arguments: object with the required/optional fields
- brief rationale explaining your choice
"""
    return guidance.strip()
