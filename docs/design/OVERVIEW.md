---
type: product_context
title: GDAL MCP Overview
tags: [design, overview, product_context]
---

# GDAL MCP Overview

## Purpose

The **Geospatial Data Abstraction Library (GDAL)** is an open-source translator library for raster and vector geospatial data formats that powers a broad ecosystem of remote-sensing and GIS tooling【666650857824669†L25-L33】. The **Model Context Protocol (MCP)** connects AI models to external systems through JSON-RPC 2.0 and formalises how tools and resources are described and invoked【326596536680505†L84-L173】. This project proposes a **GDAL MCP server** so that agents can trigger GDAL workflows under human supervision while following MCP security guarantees.

We intend to build on the **fastMCP** reference server. The framework already implements the MCP handshake, JSON-RPC routing, and a structured confirmation workflow, allowing the GDAL tooling to focus on parameter validation, subprocess execution, and resource publication instead of recreating the transport layer from scratch. fastMCP also makes it easy to ship a consistent developer experience across local and hosted deployments.

## Goals

1. **Expose GDAL utilities as MCP tools.** Each GDAL CLI command will be mapped to an MCP tool with precise JSON Schemas so that agents understand the required parameters and the shape of responses.
2. **Ensure secure, human-centred execution.** Tool invocations must surface friendly confirmation prompts, enforce path whitelisting, and log actions for auditing in line with MCP guidance【555906160256464†L154-L181】.
3. **Adopt a modular architecture.** Python wrappers will isolate command construction, validation, execution, and result handling to simplify adding new tools or adjusting behaviours over time.
4. **Support collaborative open source development.** The repository will remain MIT-licensed and include contribution guides, testing workflows, and automation hooks that streamline community participation.

## Use Cases

- **Data inspection.** Analysts can call `info` (GDAL `gdal info`) from an MCP-aware client to verify dataset quality without leaving their workspace.
- **Format conversion.** Agents convert rasters to COG, JPEG, or NetCDF via `convert` (GDAL `gdal convert`), piping results back as MCP resources for follow-up processing.
- **Spatial operations.** Complex workflows—mosaicking, reprojection (`reproject` → GDAL `gdal raster reproject`), rasterising vectors—execute under supervision while retaining a complete audit trail.
- **Automation guardrails.** Teams embed GDAL steps inside wider agent flows (e.g., report generation) while ensuring every invocation passes through fastMCP’s confirmation gate.

## Stakeholders & Responsibilities

- **Core maintainers** own architecture, release management, and schema evolution.
- **Contributors** propose new tool wrappers or improvements by following the testing and documentation guidelines in `docs/design/`.
- **Operators** deploy the packaged server via `uvx` or Docker, configure workspaces, and monitor observability signals.
- **Agent builders** integrate the MCP endpoints into their assistants, relying on the documented contracts and resources.

## Non-Goals

- Rewriting or modifying GDAL core functionality; we wrap stable CLI commands instead.
- Providing a long-running job queue or distributed execution platform in the initial release.
- Shipping bespoke GIS visualisations—outputs are delivered as files or structured JSON for downstream tools.

## Success Metrics

- **Reliability.** ≥99% success rate across CI integration runs and smoke tests for supported tools.
- **Safety.** Zero confirmed incidents of unauthorised filesystem access thanks to enforced whitelists and confirmations.
- **Adoption.** External contributors add or enhance tool wrappers following the documented processes.
- **Portability.** Users can launch the server locally with `uvx` or in Docker with identical behaviour.

## Document Map

To keep the design approachable, the content is split into focused documents:

- [Architecture](architecture.md) — how the fastMCP-based server is composed, including data flow and security controls.
- [Tool Specifications](tools.md) — JSON Schemas and behavioural notes for each GDAL command we intend to expose.
- [Testing & QA Strategy](testing.md) — validation approach to keep schemas, consent flows, and binaries reliable.
- [Distribution Strategy](distribution.md) — how to package and ship the server via `uvx`, Docker, and automated releases.

Each document is self-contained but builds toward a cohesive GDAL MCP implementation.
