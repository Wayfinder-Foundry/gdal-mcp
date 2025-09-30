---
type: product_context
title: GDAL MCP Roadmap
tags: [gdal, mcp, roadmap, planning]
---

# GDAL MCP Roadmap

This roadmap aligns with the brief in `.windsurf/workflows/config/brief.md` and the guidance in `docs/mcp-guidelines.md`.

## Milestones

- M1: Foundation & Compliance
  - ADRs: 0001 fastMCP foundation, 0002 transports (stdio/http), 0003 distribution (uvx/Docker)
  - MCP compliance checklist; initialization/versioning; capabilities; stderr logging
- M2: Core Tools (Minimum Usable Set)
  - Tools: `get_info`, `translate`, `warp`, `build_overviews`
  - Enums: reuse `server/enums/format.py`, `server/enums/resampling.py`
- M3: Docs Ingestion → ConPort
  - Frontmatter across docs; `scripts/ingest_docs.py` emits `conport_export/` and imports
- M4: Performance & Stability
  - Bench harness `scripts/bench.py`; SLOs; memory/cpu/RSS tracking; concurrency caps
- M5: Packaging & Distribution
  - uvx entrypoint `gdal-mcp`; `Dockerfile` with slim GDAL base; healthcheck
- M6: Observability & Ops
  - Structured logs to stderr, log levels, optional metrics; operations guide

## Acceptance Criteria (by milestone)

- M1: Correct init/version negotiation; declared capabilities only; no stdout logs; JSON‑schema’d tools
- M2: Friendly validation errors; deterministic temp paths; robust GDAL error mapping
- M3: Idempotent ingestion via stable IDs and content hashes; ConPort links between items
- M4: Baselines recorded; p50/p95 under thresholds; no leaks over 100 runs
- M5: `uvx gdal-mcp --help` works; Docker builds and runs; smoke test passes
- M6: Logs actionable; common failure runbooks documented

## Performance Goals (initial)

- `get_info` p95 < 500ms small; < 2s medium
- `translate` p95 < 10s medium COG
- `warp` p95 < 20s medium reprojection
- Memory steady‑state < 1.5× input for translate/warp; no leaks across 100 runs

## Next Steps

- Add `MCP-COMPLIANCE.md`, `PERFORMANCE.md`, ADRs 0001‑0003
- Create ingestion CLI & workflow; retrofit frontmatter
- Scaffold fastMCP server and tests; then packaging
