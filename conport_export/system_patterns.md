# System Patterns

---
## Frontmatter → ConPort ingestion pipeline
*   [2025-09-27 20:29:35]
*   [2025-09-18 01:09:47]
Markdown docs carry YAML frontmatter {type, id, title, tags, links}. A CLI (`gdal_mcp/ingest.py`) emits per-item Markdown to `conport_export/<type>/<slug>.md` plus an index.jsonl. ConPort import is idempotent using stable IDs and content hashes. Missing types default to `misc`.
---

---
## Hierarchical tool modules with flat tool names
*   [2025-09-27 20:29:35]
*   [2025-09-18 01:09:01]
Place tools under `gdal_mcp/tools/` with submodules for groups (e.g., `gdal_mcp/tools/raster/`). Expose MCP tool names without the `gdal_` prefix (e.g., `info`, `convert`, `reproject`). Ensure name uniqueness across the flat tool list; use dotted names if a collision occurs (e.g., `raster.reproject`).
