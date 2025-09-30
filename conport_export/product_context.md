# Product Context
## Introduction


## Deliverables
Python package gdal_mcp with FastMCP server and tools.
CLI: gdal-mcp, gdal-mcp-ingest, gdal-mcp-bench.
Docs: ROADMAP, PERFORMANCE, MCP-COMPLIANCE, ADRs 0001-0003.

## Description
MCP server exposing GDAL 3.11 unified CLI subcommands via FastMCP. Distribute via uvx and Docker. ConPort-backed docs ingestion.

## Distribution
uvx gdal-mcp
Docker image with GDAL base

## Goals
Expose core GDAL ops as safe MCP tools (info, convert, raster reproject, overview, clip).
Adhere to MCP compliance (init/version, capabilities, stderr logging).
Ship uvx entrypoint and minimal Docker image with GDAL.

## Name
GDAL MCP

## Nongoalsphase1
Full analytics suite
Async job queues
Tiling service

## Scopephase1
FastMCP server with minimal well-typed tools.
Docs ingestion pipeline to ConPort (idempotent).
Perf harness and baselines.

## Sources
README.md
docs/ROADMAP.md
docs/MCP-COMPLIANCE.md
docs/PERFORMANCE.md
docs/ADR/0001-fastmcp-foundation.md
docs/ADR/0002-transport-stdio-http.md
docs/ADR/0003-distribution-uvx-docker.md
docs/mcp-guidelines.md
docs/fastmcp-guidelines.md

