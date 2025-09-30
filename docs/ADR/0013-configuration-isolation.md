# ADR-0013-configuration-isolation.md

## Title

Per-request GDAL configuration isolation

## Status

Proposed

## Context

GDAL has global config/state that can bleed across operations.

## Decision

* Wrap each tool in `rasterio.Env(...)` (and/or GDAL config contexts) to set per-request options (`GDAL_CACHEMAX`, VSI auth, threads).
* Avoid global mutation; never rely on ambient environment.

## Consequences

* Pro: Deterministic behavior, safer multi-tenant ops.
* Con: Must plumb config options through tool params.
