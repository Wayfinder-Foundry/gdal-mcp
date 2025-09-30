---
type: decision
id: ADR-0003
title: Distribution via uvx and Docker
tags: [adr, distribution, uvx, docker]
status: accepted
 date: 2025-09-17
---

# ADR-0003: Distribution via uvx and Docker

## Context

We want one-line local execution and a reproducible container image with GDAL.

## Decision

- Provide `gdal-mcp` console entrypoint in `pyproject.toml` and distribute via `uvx`.
- Provide a minimal Docker image (GDAL base) with `ENTRYPOINT ["gdal-mcp"]` and a healthcheck.

## Consequences

- Pros: Easy local run, portable container for CI/CD and remote hosts.
- Cons: Image size considerations; need multi-arch builds.

## Status

Accepted for Phase 1.

## Links

- `docs/ROADMAP.md`
- `docs/PERFORMANCE.md`
