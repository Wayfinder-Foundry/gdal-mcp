# ADR-0010-crs-and-resampling-policy.md

## Title

CRS normalization and explicit resampling

## Status

Proposed

## Context

Ambiguous CRS/resampling cause silent quality issues.

## Decision

* Normalize CRS with `pyproj.CRS` (store as string like `EPSG:XXXX`).
* Require explicit `resampling` param with controlled enum.
* Preserve / set `nodata` explicitly; document defaults.

## Consequences

* Pro: Predictable results; auditability.
* Con: Slightly more parameters for users.
