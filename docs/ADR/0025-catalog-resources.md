---
status: proposed
date: 2025-10-10
decision-makers: [jgodau, cascade-ai]
tags: [catalog, resources, fastmcp, architecture]
---

# ADR-0025: Catalog Resource Suite for Workspace Discovery

## Context

The GDAL MCP server now exposes metadata resources for individual raster and vector files.
Agents also need a fast way to discover *which* datasets exist inside the allowed
workspace directories governed by `GDAL_MCP_WORKSPACES` and the path-validation
middleware (`src/middleware.py`).

We currently lack:

- A structured listing of workspace files categorized by type (raster/vector/other).
- A shared scanner that respects workspace boundaries, size, and filtering heuristics.
- Dedicated catalog resources to support questions like “what rasters are available?”
  before the agent chooses a tool.

## Decision

Introduce a catalog resource suite backed by a shared scanner module:

### Shared Scanner (`src/shared/catalog/scanner.py`)
- Enumerate files beneath all configured workspaces (`src/config.get_workspaces()`).
- Use suffix heuristics to classify entries as raster, vector, or other assets.
- Return lightweight dictionaries or `ResourceRef` instances with path, size, driver/type hint,
  and optional tags for planning.
- Offer filtering controls (e.g., include/exclude patterns, max depth, max results).
- Provide simple in-memory caching keyed by workspace roots and modification timestamps to
  avoid repeated directory traversal during a single session.

### Resources (`src/resources/catalog/`)
- `catalog://workspace/all` — surface every discovered asset with basic metadata.
- `catalog://workspace/raster` — subset restricted to raster-friendly extensions
  (e.g., `.tif`, `.tiff`, `.vrt`, `.nc`, `.img`).
- `catalog://workspace/vector` — subset restricted to vector formats
  (e.g., `.geojson`, `.json`, `.gpkg`, `.shp`, `.kml`).
- Resources accept optional query parameters (e.g., `limit`, `extensions`, `include_hidden`).
- Resources enforce path validation by leaning on the shared scanner and never bypassing the middleware.

### Logging & Context (per ADR-0024)
- Resources log boundary messages only (start/end, summary) and rely on `ctx` for
  progress if scanning becomes long-running.
- The scanner itself remains silent unless `ctx` is passed explicitly for debugging.

## Consequences

- **Positive**: Agents gain immediate visibility into available datasets, enabling
  richer prompts and automated workflows. The shared scanner consolidates workspace
  traversal logic, reducing duplication across future features (e.g., previews, indexing).
- **Negative**: Requires careful performance tuning for very large workspaces;
  may need throttling or pagination in future iterations.
- **Neutral**: Classification heuristics start simple (extension-based) and can be
  refined later with content sniffing if needed.

## Status

Proposed — implementation in progress.
