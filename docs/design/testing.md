---
type: product_context
title: Testing & QA Strategy
tags: [design, testing, qa, product_context]
---

# Testing & QA Strategy

Maintaining trust in the GDAL MCP server requires disciplined validation across function signatures, subprocess command composition, runtime contracts, and distribution artefacts. This guide captures the quality approach for contributors.

## Guiding Principles

- **Reproducibility first.** Deterministic tests with pinned deps, small fixtures, and isolated temp dirs.
- **FastMCP parity.** Preserve compatibility with FastMCP transports (stdio/http), confirmation, and error envelopes.
- **Shift-left validation.** Validate function inputs and CLI argument assembly before invoking GDAL.
- **Security preservation.** Exercise consent flows and path validation to uphold MCP security guidelines.
- **Automation friendly.** All checks run in CI with clear pass/fail signals and uploaded logs.

## Test Layers

### 1. Static & Linting

- `ruff` for style/import hygiene and subprocess safety rules.
- `mypy` with strict optional on tool modules and helpers (`gdal_mcp/utils.py`).
- Optional: generate and snapshot FastMCP-derived schemas from type hints to detect breaking changes.

### 2. Unit Tests

- Validate each wrapper’s CLI assembly without calling GDAL (patch `run_gdal`).
- Confirm defaults and optional parameters are respected.
- Test error surfacing: non‑zero exit codes raise with concise messages.

### 3. Integration Tests

- Start an in‑process FastMCP server via `uv run gdal-mcp serve --transport stdio` and use fixtures under `test/data/`.
- Exercise tools against tiny rasters:
  - `info` (JSON and text)
  - `convert` (format + CO options)
  - `reproject` (dst CRS, resampling)
- Parametrise edge cases: missing inputs, timeouts, and overwrite paths.
- For HTTP, assert response envelopes and headers.

### 4. Contract Tests

- Snapshot tool metadata from `tools/list` and diff in CI to catch accidental name/signature changes.
- Validate example `tools/call` requests and responses for each tool.

### 5. Security & Compliance

- Block directory traversal (`..`) and unexpected absolute paths where applicable.
- Ensure no stdout prints from server; logs go to stderr.
- Dependency vuln scanning (`uv audit` or `pip-audit`).

### 6. Performance (Smoke)

- Use `gdal_mcp/bench.py` for a tiny reprojection smoke to track wall time.
- Record p50/p95 and stderr size to detect regressions.

## Tooling & Automation

- Local: `uv run ruff check`, `uv run mypy`, and `uv run pytest -q`.
- CI stages: `lint`, `type-check`, `unit`, `integration`, `package-smoke` (build wheel + `uvx gdal-mcp --help`).
- Failures attach server stderr logs for triage.

## Release Gates

- Green CI, Docker smoke (`gdalinfo --version`), and `uvx gdal-mcp --help` verified.
- Update `CHANGELOG.md` noting tool signature changes.

Adhering to this strategy keeps the server dependable while enabling rapid iteration across tools and distribution.
