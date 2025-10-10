# FastMCP Context Usage Guide

This guide describes how GDAL MCP uses the FastMCP `Context` object and how to
keep logging and orchestration consistent across tools, resources, and shared
modules.

## 1. Where Context Lives

- **Entry points only**: `Context` is injected into MCP tools, resources, and
  prompts (`src/tools/`, `src/resources/`, `src/prompts/`). These functions own
  logging, progress reporting, and request metadata access.
- **Shared helpers**: Modules under `src/shared/` accept `ctx: Context | None`
  but remain silent unless the caller explicitly opts in. This keeps shared
  logic reusable outside MCP and avoids duplicate logging.

## 2. Allowed Operations

When using `Context`, limit usage to:

- Logging via `ctx.info`, `ctx.debug`, `ctx.warning`, `ctx.error`.
- Reporting progress with `ctx.report_progress(progress, total, message?)`.
- Reading resources (`await ctx.read_resource(uri)`).
- Accessing request metadata (`ctx.request_id`, `ctx.client_id`).
- Managing per-request scratch state (`ctx.set_state`, `ctx.get_state`).
- Optional LLM sampling (`await ctx.sample(prompt)`) when a tool needs
  on-the-fly assistance.

## 3. Prohibited Operations

Avoid the following to prevent `Context` from becoming a god object:

- Persisting state across requests or mutating global config.
- Embedding business logic or decision-making inside Context helpers.
- Transporting large datasets or binary payloads via context state/logs.
- Performing blocking IO inside context helper wrappers.

## 4. Logging Patterns

- **Log at the boundary**: Entry points announce start/end, key milestones, and
  recoverable errors.
- **No duplicates**: Shared helpers remain silent by default. If deeper logging
  is required, pass `ctx` explicitly and emit curated messages only.
- **Consistency**: Prefix messages (e.g., `[raster_info] Converting ...`) so log
  consumers can filter quickly.
- **Signal over noise**: Prefer progress updates over repetitive info messages
  in tight loops.

## 5. Passing Context to Helpers

When helpers need logging or progress reporting, pass `ctx` explicitly:

```python
from src.shared.raster.info import info as raster_info_core

@mcp.tool
async def raster_info(uri: str, ctx: Context | None = None) -> RasterInfo:
    await ctx.info("[raster_info] Starting")  # Boundary log
    data = raster_info_core(uri, ctx=ctx)     # Helper remains optional
    return RasterInfo(**data)
```

If a helper is called without `ctx`, it should still succeed and stay silent.

## 6. Review Checklist

Before merging changes:

- Logging occurs only at entry points or deliberately opted-in helpers.
- All `ctx.` usage appears in modules cleared for orchestration responsibilities.
- Shared modules accept `ctx: Context | None` but do not require it.
- No business logic or configuration lives inside context helper functions.

This policy keeps MCP logs meaningful, maintains a clean separation between
control flow and domain logic, and preserves the ability to reuse shared modules
outside the MCP runtime.
