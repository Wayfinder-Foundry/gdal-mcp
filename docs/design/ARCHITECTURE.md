---
type: product_context
title: Architecture
tags: [design, architecture, product_context]
---

# Architecture

## System Overview

The server is built on FastMCP and exposes a small set of GDAL commands via de-facto pythonic gdal-based libraries as MCP tools. FastMCP handles JSON‑RPC routing, schema generation from type hints/docstrings, and transports (stdio, HTTP). We focus on parameter validation, safe subprocess execution, and clear, structured results.

Core runtime pieces include:

1. **JSON‑RPC server.** FastMCP runs over stdio (default) or HTTP. We register tool handlers in the `tools` namespace.
2. **Tools.** Implementations that mirror common gdal binaries using pythonic libraries rasterio and shapely for raster and vector operations, respectively. 
3. **Resource publication.** File‑producing tools register outputs as file:// resources (via `mcp.add_resource(FileResource(...))`). Currently implemented in `convert()` and `reproject()`. `info()` does not produce files and returns structured output only.
4. **Consent & safety.** All executions rely on host‑side user approval (FastMCP confirmation). Logging goes to stderr only.

## Execution Lifecycle

1. Client connects and negotiates capabilities (handled by FastMCP).
2. Client lists tools (`tools/list`) and calls a tool with validated arguments (`tools/call`).
3. On success, structured results are returned; on failure, a clear error is raised.

## Security & Trust

- **Least privilege:** Only subprocess execution; no stdout logging, no implicit filesystem writes outside user‑provided paths.
- **Consent:** Hosts must obtain user approval before any tool call.
- **Validation:** Type‑hinted inputs map to generated schemas; wrappers avoid mutating state unless explicitly requested (e.g., `--overwrite`).

## Observability

- **Logging:** Structured logs to stderr with levels (configurable via CLI log level).
- **Benchmarks:** `bench.py` provides a smoke reprojection run for quick timing.

## Extensibility

- Add new wrappers under `gdal_mcp/tools/` (or a subgroup) and decorate with `@mcp.tool`.
- For overlapping names (e.g., vector `reproject`), adopt dotted names like `raster.reproject`/`vector.reproject` to retain uniqueness.
