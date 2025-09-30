# 0004-adopt-fastmcp-and-python-native-stack.md

## Title

Adopt FastMCP and a Python-native GDAL stack (rasterio + pyogrio/fiona + pyproj)

## Status

Proposed

## Context

We’re building a GDAL MCP server. Two options exist: wrap CLI tools (`gdalwarp`, `gdal_translate`, etc.) or use Python bindings (rasterio/pyogrio/fiona/pyproj + selective GDAL/OGR fallback). MCP benefits from typed params, structured outputs, progress, and error control.

## Decision

Use **FastMCP** with a **Python-native stack**:

* **Raster**: `rasterio` (+ `pyproj`) as the default; fall back to `osgeo.gdal` only when required.
* **Vector**: prefer **pyogrio** (fast, Arrow-native) or **fiona** for stability; fall back to `osgeo.ogr` for exotic cases.

## Consequences

* Pro: Structured I/O, easier progress/cancel, safer error handling, fewer shell/security headaches, cleaner MCP UX.
* Con: Must manage native wheels for rasterio/pyogrio; occasional gaps vs. newest CLI features.

