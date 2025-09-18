---
type: product_context
title: Tool Specifications
tags: [design, tools, product_context]
---

# Tool Specifications

This document defines the current MCP tools exposed by the GDAL MCP server, their parameters, and behaviour. Tools are implemented as Python functions decorated with `@mcp.tool` and live under the hierarchical package `gdal_mcp/tools/`. The MCP tool list is flat, so function names must be unique.

- Module layout:
  - `gdal_mcp/tools/info.py` → `info()` wraps `gdal info`
  - `gdal_mcp/tools/convert.py` → `convert()` wraps `gdal convert`
  - `gdal_mcp/tools/raster/reproject.py` → `reproject()` wraps `gdal raster reproject`

Schemas are generated automatically from type hints and docstrings by FastMCP.

## Conventions

- Paths must be valid on the server host; relative paths are resolved by the GDAL subprocess.
- Optional arguments are omitted from the CLI unless provided.
- All logging goes to stderr; returned payloads are structured JSON.
- Errors raise with a concise message derived from GDAL stderr, surfaced to the MCP host.

---

## info()

Wraps: `gdal info`

- Parameters
  - `path: str` — Input dataset path or URI
  - `format: str = "json"` — One of `json`, `text`

- Behaviour
  - Constructs: `gdal info <path> --format <json|text>`
  - On success:
    - If `format=json`, parses stdout to a dict and returns it.
    - If `format=text`, returns `{ "text": <stdout> }`.
  - On failure: raises `RuntimeError` with GDAL stderr (or stdout fallback).

- Returns (examples)
  - JSON format: the parsed GDAL info structure
  - Text format: `{ "text": "..." }`

---

## convert()

Wraps: `gdal convert`

- Parameters
  - `input: str` — Source dataset path/URI
  - `output: str` — Output path/URI
  - `output_format: Optional[str] = None` — Driver short name (e.g., `GTiff`, `COG`, `GPKG`)
  - `overwrite: bool = True` — Add `--overwrite`
  - `creation_options: Optional[Dict[str,str]] = None` — Emits repeated `--creation-option key=value`
  - `extra_args: Optional[List[str]] = None` — Additional CLI switches appended verbatim

- Behaviour
  - Constructs: `gdal convert <input> <output> [--output-format <drv>] [--overwrite] [--creation-option k=v]* [extra...]`
  - On success: returns `{ "output": <output>, "resource_uri": <file://...>|null, "stderr": <err> }` (stderr typically contains GDAL progress/messages). `resource_uri` is set when the output file exists and is registered as a resource.
  - On failure: raises `RuntimeError` with GDAL stderr

- Notes
  - Creation options are driver-specific (e.g., `TILED=YES`, `COMPRESS=ZSTD`).

---

## reproject()

Wraps: `gdal raster reproject`

- Parameters
  - `input: str` — Source raster
  - `output: str` — Output raster
  - `dst_crs: str` — Destination CRS (e.g., `EPSG:4326`)
  - `src_crs: Optional[str] = None`
  - `resampling: Optional[str] = None` — e.g., `near`, `bilinear`, `cubic`, ...
  - `resolution: Optional[str] = None` — `<xres>,<yres>`
  - `size: Optional[str] = None` — `<width>,<height>` (mutually exclusive with `resolution`)
  - `bbox: Optional[str] = None` — `<xmin>,<ymin>,<xmax>,<ymax>` in `bbox_crs` if set else `dst_crs`
  - `bbox_crs: Optional[str] = None`
  - `overwrite: bool = True`
  - `creation_options: Optional[Dict[str,str]] = None` — `--creation-option k=v`
  - `warp_options: Optional[Dict[str,str]] = None` — `--warp-option k=v`
  - `transform_options: Optional[Dict[str,str]] = None` — `--transform-option k=v`
  - `extra_args: Optional[List[str]] = None`

- Behaviour
  - Constructs: `gdal raster reproject <input> <output> --dst-crs <dst> [--src-crs <src>] [--resampling <alg>] [--resolution <r>] [--size <w,h>] [--bbox <...>] [--bbox-crs <...>] [--overwrite] [--creation-option k=v]* [--warp-option k=v]* [--transform-option k=v]* [extra...]`
  - On success: `{ "output": <output>, "resource_uri": <file://...>|null, "stderr": <err> }`
  - On failure: raises `RuntimeError` with stderr

- Tips
  - Use `resolution` OR `size`, not both.
  - `warp_options` and `transform_options` pass directly to the underlying GDAL warp/transform.

---

## Future candidates (not yet implemented)

- Raster: `overview add/delete`, `clip`, `translate` options expansion.
- Vector: `info`, `reproject`, `clip`, `convert`.

Adding a tool follows the same pattern: new module under `gdal_mcp/tools/` (or a subgroup), `@mcp.tool` with typed signature, and a subprocess assembly mirroring the GDAL 3.11 CLI.
