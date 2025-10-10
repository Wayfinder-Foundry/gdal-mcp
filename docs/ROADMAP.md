---
type: product_context
title: GDAL MCP Roadmap
tags: [gdal, mcp, roadmap, planning]
---

## Milestones

- M1: Foundation & Compliance
  - ADRs: 0001 fastMCP foundation, 0002 transports (stdio/http), 0003 distribution (uvx/Docker)
  - MCP compliance checklist; initialization/versioning; capabilities; stderr logging
- M2: Core Tools (Minimum Usable Set)
  - Tools: `get_info`, `translate`, `warp`, `build_overviews`
  - Enums: reuse `server/enums/format.py`, `server/enums/resampling.py`
- M3: Packaging & Distribution
  - uvx entrypoint `gdal-mcp`; `Dockerfile` with slim GDAL base; healthcheck
- M4: Observability & Ops
  - Structured logs to stderr, log levels, optional metrics; operations guide
- M5: Resource Taxonomy (ADR-0023)
  - **Phase 2A (Done / v0.2.0)**: catalog discovery resources, metadata format resource, reference knowledge base
  - Phase 2B: workspace summaries, CRS-indexed catalog views, extended metadata stats
  - Phase 2C: context/history resources (session state, provenance)
  - Phase 2D: domain references & terrain toolkits (resampling/compression guides, terrain parameters)

## Next Steps

- Phase 2B discovery enhancements: `catalog://workspace/by-crs/{epsg}`, workspace summaries, richer metadata statistics.
- Phase 2C context/history work: `context://session/current`, `history://operations/...` for multi-step continuity.
- Phase 2D domain references: terrain analysis guides, format primers, expanded glossary entries.
- Automate prompt regression harness using `test/prompt_suite/test_prompts.py` to capture before/after transcripts.
- Continue documentation cadence: finalize `docs/fastmcp/RESOURCES.md` and promote ADR-0025 to accepted once Phase 2B ships.
