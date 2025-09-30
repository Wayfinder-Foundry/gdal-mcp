---
type: decision
id: ADR-0001
title: FastMCP foundation for GDAL MCP (Python)
tags: [adr, fastmcp, python, mcp, server]
status: accepted
 date: 2025-09-17
---

# ADR-0001: FastMCP foundation for GDAL MCP (Python)

## Context

We need a compliant MCP server to expose GDAL capabilities. Python offers mature GDAL bindings and the `mcp.server.fastmcp` SDK for rapid, type-annotated tool definition and stdio transport. Alternatives (TypeScript/Go) increase integration cost with GDAL.

## Decision

- Use Python and `mcp.server.fastmcp` to implement the server.
- Default transport: stdio; optional HTTP transport may be added later.
- Follow `docs/mcp-guidelines.md` for compliance (init/versioning, capabilities, stderr logging).

## Consequences

- Pros: Fast iteration, strong GDAL ecosystem, simpler packaging with uv/uvx.
- Cons: Python runtime in Docker; require careful perf tuning for large rasters.

## Status

Accepted for Phase 1.

## Links

- `docs/MCP-COMPLIANCE.md`
- `docs/ROADMAP.md`
