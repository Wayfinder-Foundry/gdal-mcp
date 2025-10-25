Project Brief (concise)
Goal: Build a standards-compliant MCP server that exposes core GDAL capabilities (inspect, translate, warp/reproject, resample, clip/crop, convert formats), with good UX for devtools and automations.
Users: ML/Data eng, GIS analysts, AI agents needing geospatial transforms at scale with reproducible configs.
Scope (Phase 1):
fastMCP server exposing minimal, well-typed tools:
info/metadata, translate (format/creationOptions), warp (dstSRS, resampling, cutline), overview build, gcp/reprojection helpers.
Controlled outputs: file, stream, or in-memory bytes where practical.
Enum safety: reuse Format and Resampling from server/enums/.
Deterministic temp paths & cleanup; error reporting with GDAL error class capture.
Docs ingestion pipeline to ConPort (architecture, decisions, patterns, glossary).
Distribution via uvx and Docker, with GDAL binaries/runtime.
Non-goals (Phase 1): Full raster/vector analytics, tiling services, catalog/search, async job queue.
Deliverables:
fastMCP server package gdal_mcp with tools (API docstrings + tests).
CLI gdal-mcp to run server locally (for uvx and Docker entrypoint).
Docs ingester CLI that syncs docs/ → ConPort (idempotent).
Minimal examples in test/demo_gdal_mcp.py and pytest coverage.
Quality: Type hints, small composable functions, clear error messages, hermetic tests where possible.
Distribution: uvx gdal-mcp and a slim Docker image with GDAL + server.
Ingestion Plan for docs/
Objectives
Parse markdown in docs/ and map to ConPort entities:
Product/Architecture context, Decisions (ADRs), System Patterns, Glossary, Usage.
Idempotently upsert, tag, and link items. Generate ConPort-ready artifacts for import.
Source Inventory and Mapping
docs/design/index.md → Product summary (vision/scope).
docs/design/architecture.md → Product context (components, flows, constraints).
docs/design/distribution.md → Product context (packaging/deploy).
README.md → Product context (intro, quickstart).
GDAL_MCP_USAGE.md → Usage notes → Custom Data category “ProjectUsage”.
Future ADRs: docs/adr/NNN-*.md → Decisions.
Patterns: docs/patterns/*.md (to be added) → System Patterns.
Glossary: docs/glossary.md (to be added) → Custom Data category “ProjectGlossary”.
Authoring Conventions (lightweight)
Add YAML frontmatter to each doc:
type: product_context | decision | system_pattern | glossary | usage
title: ...
tags: [gdal, mcp, server, packaging, ...]
Optional linking: links: [{type: 'relates_to' | 'implements' | 'supersedes', target: 'id-or-title'}]
Optional stable id: id: ADR-0001 (for decisions) or pattern: Name.
For ADRs: sections “Context”, “Decision”, “Consequences”, “Status”.
Transformation Pipeline (CLI)
Tool: scripts/ingest_docs.py (or tools/ingest_docs.py)
Behavior:
Walk docs/ and selected top-level files (README.md, GDAL_MCP_USAGE.md).
Parse frontmatter (fallback heuristics if absent based on path/headers).
Normalize into ConPort model payloads:
Product Context: consolidate into a structured JSON with sections.
Decisions: summary, rationale, implementation_details, tags.
System Patterns: name, description, tags.
Glossary/Usage: key/value entries under categories.
Compute content hash to support idempotent upserts (store .cache/ingest-index.json).
Emit ConPort Markdown artifacts into ./conport_export/ (one file per item + an aggregated product context).
Option A (preferred): I call ConPort import tool to ingest artifacts.
Option B: script prints a summary and you trigger import via workflow.
CLI flags:
--root docs/, --only types (comma list), --since <date>, --dry-run, --verbose.
--emit conport_export/ (default), --no-import to skip auto-import.
ConPort Operations
Import path: use ConPort’s import to read ./conport_export/.
For incremental updates: patch product context via merges; upsert decisions/patterns by stable id or title; add tags: docs_source:<relpath>, gdal, mcp, version:<x>.
Create relationships via link metadata:
ADRs “implements/affects” product sections.
Patterns “used_by” decisions.
Usage docs “relates_to” product context.
Idempotency & Safety
Stable IDs from frontmatter or filename; hash of normalized content.
Dry-run prints planned creates/updates/links.
No deletes by default; --prune optional to archive or mark stale.
Minimal Dependencies
python-frontmatter, markdown-it-py (or mdpo alternative), pyyaml.
No network calls required; emits markdown for ConPort import.
Workflows
Add a Windsurf workflow /ingest shortcut that runs the CLI and then calls ConPort import.
Nightly CI optional to enforce docs ↔ ConPort sync.
fastMCP Integration Outline
Server package: server/ evolves to a fastMCP app gdal_mcp:
Tools:
get_info(path) → metadata, srs, size, bbox.
translate(src, dst, format: Format, creation_options: dict).
warp(src, dst, dst_srs, resampling: Resampling, cutline=None, bbox=None, dst_res=None).
build_overviews(src, resampling: Resampling, levels=None).
Use enums in server/enums/format.py, server/enums/resampling.py.
Temp handling: TMPDIR/gdal-mcp/<jobId>/..., cleanup on success/failure.
Error capture: map GDAL error levels to MCP errors with actionable messages.
Config: env-driven (GDAL_DATA, PROJ, cache dirs), logging config.
Docs: docstrings + examples mirrored in test/demo_gdal_mcp.py.
Distribution Plan
uvx executable:
Provide console entry point gdal-mcp that launches the fastMCP server.
Ensure pyproject.toml has [project.scripts] gdal-mcp = "gdal_mcp.__main__:main".
Publish under a pinned version; verified with uvx gdal-mcp@<ver>.
Docker:
Base on a slim GDAL image (e.g., osgeo/gdal:alpine-small-latest or ghcr.io/osgeo/gdal minimal).
Install Python + project deps; ENTRYPOINT ["gdal-mcp"].
Expose server port; healthcheck endpoint.
Multi-arch build via buildx; small attack surface.
Recommended Actions
[Enable FS access] Add /home/jgodau/work/personal/gdal-mcp to the filesystem MCP allowed directories so I can automate scans/edits.
[Confirm brief] Approve the Project Brief above or suggest changes.
[Docs ingestion] Approve the ingestion plan and frontmatter convention. I’ll then:
Add frontmatter to existing docs where missing.
Scaffold scripts/ingest_docs.py and a /ingest workflow.
Generate conport_export/ and import into ConPort.
[fastMCP scaffold] Create the server package with initial tools using the existing enums.
[Packaging] Add uvx entrypoint + Dockerfile; wire CI to build and test.